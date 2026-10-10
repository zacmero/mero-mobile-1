import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.Enumeration;
import javax.microedition.io.Connector;
import javax.microedition.io.CommConnection;
import javax.microedition.io.Connection;
import javax.microedition.io.StreamConnection;
import javax.microedition.io.file.FileConnection;
import javax.microedition.io.file.FileSystemRegistry;
import javax.microedition.lcdui.Command;
import javax.microedition.lcdui.CommandListener;
import javax.microedition.lcdui.Display;
import javax.microedition.lcdui.Displayable;
import javax.microedition.lcdui.Form;
import javax.microedition.lcdui.List;
import javax.microedition.midlet.MIDlet;

public final class MeroFiles extends MIDlet implements CommandListener, Runnable {
    private final Command exit = new Command("Exit", Command.EXIT, 1);
    private List roots;
    private Form status;
    private volatile boolean stopped;
    private boolean running;
    private String directory;
    private String ack = "none";
    private String result = "startup";
    private int sequence;
    private String commandStatus = "not checked";
    private String inboxStatus = "not checked";
    private String capabilities = "";
    private String serialReport = "serial_status=not tested\n";
    private String pathReport = "path_status=not tested\n";

    protected void startApp() {
        if (roots == null) {
            roots = new List("MERO FILES v0.8 - storage", List.IMPLICIT);
            roots.addCommand(exit);
            roots.setCommandListener(this);
            try {
                Enumeration entries = FileSystemRegistry.listRoots();
                while (entries.hasMoreElements()) roots.append((String) entries.nextElement(), null);
                if (roots.size() == 0) show("No storage roots available");
                else Display.getDisplay(this).setCurrent(roots);
            } catch (Exception error) { show(error.toString()); }
        }
    }

    public void commandAction(Command command, Displayable displayable) {
        if (command == exit) { stopped = true; notifyDestroyed(); }
        else if (command == List.SELECT_COMMAND && !running) {
            directory = "file:///" + roots.getString(roots.getSelectedIndex()) + "MeroMailbox/";
            running = true;
            new Thread(this).start();
        }
    }

    private void show(String message) {
        status = new Form("MERO FILES v0.8");
        status.append(message);
        status.addCommand(exit);
        status.setCommandListener(this);
        Display.getDisplay(this).setCurrent(status);
    }

    public void run() {
        String stage = "create mailbox";
        try {
            FileConnection folder = (FileConnection) Connector.open(directory);
            try {
                if (!folder.exists()) folder.mkdir();
                if (!folder.isDirectory()) throw new java.io.IOException("Mailbox is not a directory");
            } finally { folder.close(); }
            stage = "collect capabilities";
            capabilities = collectCapabilities();
            stage = "write startup diagnostics";
            writeResponse();
            show("Mailbox ready\n" + directory + "\nReading Ebook/command.txt");
            while (!stopped) {
                stage = "read command";
                String previousStatus = commandStatus;
                String message = readCommand();
                commandStatus = message == null ? inboxStatus : "read " + message.length() + " chars; protocol=" + field(message, "protocol") + "; end=" + message.endsWith("end=1\n");
                if (message != null && field(message, "protocol").equals("mero-files/1")
                        && message.endsWith("end=1\n")) {
                    String id = field(message, "id");
                    String command = field(message, "command");
                    if (id.length() > 0 && id.length() <= 64 && !id.equals(ack)
                            && (command.equals("PING") || command.equals("INFO") || command.equals("SERIAL") || command.equals("PATHS"))) {
                        commandStatus = "accepted " + command;
                        ack = id;
                        if (command.equals("SERIAL")) {
                            stage = "probe Java serial";
                            serialReport = probeSerial();
                            result = "SERIAL DONE";
                        } else if (command.equals("PATHS")) {
                            stage = "probe filesystem routes";
                            pathReport = probePaths();
                            result = "PATHS DONE";
                        } else result = command.equals("PING") ? "PONG" : "INFO OK";
                        stage = "write response";
                        writeResponse();
                        show("Mailbox ready\n" + directory + "\n" + command + ": " + result);
                    }
                }
                if (!commandStatus.equals(previousStatus)) {
                    stage = "write command status";
                    writeResponse();
                    show("Mailbox ready\n" + directory + "\n" + commandStatus);
                }
                Thread.sleep(2000);
            }
        } catch (Exception error) { if (!stopped) show("Failed at " + stage + "\n" + error.toString()); }
    }

    private String readCommand() throws Exception {
        FileConnection file = (FileConnection) Connector.open(directory.substring(0, directory.length() - "MeroMailbox/".length()) + "Ebook/command.txt");
        try {
            if (!file.exists()) {
                FileConnection parent = (FileConnection) Connector.open(directory.substring(0, directory.length() - "MeroMailbox/".length()) + "Ebook/");
                try { inboxStatus = "command missing; parent_exists=" + parent.exists() + "; url=" + file.getURL(); }
                finally { parent.close(); }
                return null;
            }
            long size = file.fileSize();
            inboxStatus = "command exists; bytes=" + size + "; url=" + file.getURL();
            if (size < 0 || size > 4096) return null;
            InputStream input = file.openInputStream();
            try {
                ByteArrayOutputStream bytes = new ByteArrayOutputStream();
                for (int i = 0; i < (int) size; i++) {
                    int c = input.read();
                    if (c == -1) throw new java.io.IOException("Command truncated at byte " + i);
                    bytes.write(c);
                }
                return new String(bytes.toByteArray(), "UTF-8");
            } finally { input.close(); }
        } finally { file.close(); }
    }

    private void writeResponse() throws Exception {
        FileConnection file = (FileConnection) Connector.open(directory + "response.txt");
        try {
            if (!file.exists()) file.create();
            file.truncate(0);
            OutputStream output = file.openOutputStream();
            try { output.write(info().getBytes("UTF-8")); output.flush(); }
            finally { output.close(); }
        } finally { file.close(); }
    }

    private String info() {
        Runtime vm = Runtime.getRuntime();
        sequence++;
        return "protocol=mero-files/1\nseq=" + sequence + "\nack=" + ack + "\nresult=" + result
            + "\ninbox_status=" + inboxStatus + "\ncommand_status=" + commandStatus + "\nmailbox=" + directory + "\nconfig=" + property("microedition.configuration")
            + "\nprofiles=" + property("microedition.profiles") + "\nplatform=" + property("microedition.platform")
            + "\nlocale=" + property("microedition.locale") + "\nheap_free=" + vm.freeMemory()
            + "\nheap_total=" + vm.totalMemory() + "\ncolors=" + Display.getDisplay(this).numColors()
            + "\nfileconnection_version=" + property("microedition.io.file.FileConnection.version")
            + "\nmedia_version=" + property("microedition.media.version")
            + "\napp_version=0.8\nphone_time_ms=" + System.currentTimeMillis()
            + "\n" + capabilities + serialReport + pathReport + "end=1\n";
    }

    private String probePaths() throws Exception {
        String[] urls = { "file:///E:/", "file:///C:/", "file:///D:/", "file:///A:/",
            "file:///F:/", "file:///Z:/", "gfs://java/3.jar" };
        StringBuffer data = new StringBuffer();
        for (int i = 0; i < urls.length && !stopped; i++) {
            PathProbe probe = new PathProbe(urls[i], i);
            new Thread(probe).start();
            long deadline = System.currentTimeMillis() + 8000;
            while (!probe.finished && !stopped && System.currentTimeMillis() < deadline) Thread.sleep(100);
            if (!probe.finished) {
                probe.cancelled = true;
                try { if (probe.connection != null) probe.connection.close(); } catch (Exception error) { }
                data.append("path_").append(i).append("_url=").append(urls[i]).append('\n');
                data.append("path_").append(i).append("_status=timeout\npath_status=stopped at timeout\n");
                return data.toString();
            }
            data.append(probe.report);
        }
        return data.append("path_status=done\n").toString();
    }

    private final class PathProbe implements Runnable {
        final String url;
        final int number;
        volatile boolean finished;
        volatile boolean cancelled;
        volatile Connection connection;
        String report;
        PathProbe(String url, int number) { this.url = url; this.number = number; }
        public void run() {
            String prefix = "path_" + number + "_";
            StringBuffer data = new StringBuffer(prefix + "url=" + url + "\n");
            try {
                connection = Connector.open(url);
                if (cancelled) return;
                data.append(prefix).append("class=").append(connection.getClass().getName()).append('\n');
                if (connection instanceof FileConnection) {
                    FileConnection file = (FileConnection) connection;
                    data.append(prefix).append("exists=").append(file.exists()).append('\n');
                    if (file.exists()) data.append(prefix).append("directory=").append(file.isDirectory()).append('\n');
                }
                if (url.equals("gfs://java/3.jar") && connection instanceof StreamConnection) {
                    InputStream input = ((StreamConnection) connection).openInputStream();
                    try {
                        StringBuffer hex = new StringBuffer();
                        String digits = "0123456789abcdef";
                        for (int i = 0; i < 16 && !cancelled; i++) {
                            int c = input.read();
                            if (c < 0) break;
                            hex.append(digits.charAt((c & 255) >> 4)).append(digits.charAt(c & 15));
                        }
                        data.append(prefix).append("owned_jar_header_hex=").append(hex).append('\n');
                    } finally { input.close(); }
                }
                data.append(prefix).append("status=opened\n");
            } catch (Exception error) {
                data.append(prefix).append("status=error\n");
                data.append(prefix).append("error=").append(error.toString().replace('\n', ' ').replace('\r', ' ')).append('\n');
            } finally {
                try { if (connection != null) connection.close(); } catch (Exception error) { }
                report = data.toString();
                finished = true;
            }
        }
    }

    private String probeSerial() throws Exception {
        SerialProbe probe = new SerialProbe();
        Thread worker = new Thread(probe);
        worker.start();
        long deadline = System.currentTimeMillis() + 10000;
        while (!probe.finished && !stopped && System.currentTimeMillis() < deadline) Thread.sleep(100);
        if (!probe.finished) {
            probe.cancelled = true;
            try { if (probe.connection != null) probe.connection.close(); } catch (Exception error) { }
            return "serial_status=timeout\nserial_stage=" + probe.stage + "\n";
        }
        return probe.report;
    }

    private final class SerialProbe implements Runnable {
        volatile boolean finished;
        volatile boolean cancelled;
        volatile CommConnection connection;
        volatile String stage = "open comm:0";
        String report;
        public void run() {
            InputStream input = null;
            OutputStream output = null;
            StringBuffer data = new StringBuffer("serial_port=0\n");
            try {
                connection = (CommConnection) Connector.open("comm:0;blocking=off");
                if (cancelled) return;
                data.append("serial_baudrate=").append(connection.getBaudRate()).append('\n');
                stage = "open serial streams";
                input = connection.openInputStream();
                output = connection.openOutputStream();
                String[] commands = { "", "AT", "ATI", "AT+CGMI", "AT+CGMM", "AT+CGMR" };
                for (int i = 0; i < commands.length && !cancelled; i++) {
                    stage = i == 0 ? "passive serial read" : commands[i];
                    if (i > 0) { output.write((commands[i] + "\r").getBytes("UTF-8")); output.flush(); }
                    StringBuffer hex = new StringBuffer();
                    String digits = "0123456789abcdef";
                    long deadline = System.currentTimeMillis() + 700;
                    while (!cancelled && System.currentTimeMillis() < deadline && hex.length() < 1024) {
                        if (input.available() > 0) {
                            int c = input.read();
                            if (c < 0) break;
                            hex.append(digits.charAt((c & 255) >> 4)).append(digits.charAt(c & 15));
                        } else Thread.sleep(50);
                    }
                    data.append("serial_reply_").append(i).append("_hex=").append(hex).append('\n');
                }
                data.append("serial_status=connected\n");
            } catch (Exception error) {
                data.append("serial_status=error\nserial_stage=").append(stage).append('\n');
                data.append("serial_error=").append(error.toString().replace('\n', ' ').replace('\r', ' ')).append('\n');
            } finally {
                try { if (input != null) input.close(); } catch (Exception error) { }
                try { if (output != null) output.close(); } catch (Exception error) { }
                try { if (connection != null) connection.close(); } catch (Exception error) { }
                report = data.toString();
                finished = true;
            }
        }
    }

    private String collectCapabilities() {
        StringBuffer data = new StringBuffer();
        String[] properties = { "microedition.encoding", "microedition.commports",
            "java.vendor", "java.version", "os.name", "os.version", "os.arch",
            "supports.audio.capture", "supports.video.capture", "supports.recording",
            "audio.encodings", "video.encodings", "video.snapshot.encodings", "streamable.contents",
            "microedition.pim.version", "microedition.location.version", "microedition.m3g.version",
            "microedition.amms.version", "microedition.sensor.version", "bluetooth.api.version" };
        for (int i = 0; i < properties.length; i++)
            data.append("property.").append(properties[i]).append('=').append(property(properties[i])).append('\n');
        String[] classes = { "javax.microedition.io.file.FileConnection", "javax.microedition.media.Manager",
            "javax.microedition.media.control.VideoControl", "javax.microedition.media.control.RecordControl",
            "javax.bluetooth.LocalDevice", "javax.obex.ClientSession", "javax.microedition.io.CommConnection",
            "javax.microedition.pim.PIM", "javax.microedition.location.LocationProvider",
            "javax.microedition.m3g.Graphics3D", "javax.microedition.sensor.SensorManager" };
        for (int i = 0; i < classes.length; i++) {
            boolean available;
            try { Class.forName(classes[i]); available = true; }
            catch (Throwable error) { available = false; }
            data.append("class.").append(classes[i]).append('=').append(available).append('\n');
        }
        for (int i = 0; i < roots.size(); i++)
            data.append("storage_root_").append(i).append('=').append(roots.getString(i)).append('\n');
        try {
            FileConnection storage = (FileConnection) Connector.open(directory);
            try {
                data.append("storage_total_bytes=").append(storage.totalSize()).append('\n');
                data.append("storage_available_bytes=").append(storage.availableSize()).append('\n');
                data.append("storage_used_bytes=").append(storage.usedSize()).append('\n');
            } finally { storage.close(); }
        } catch (Exception error) {
            data.append("storage_error=").append(error.toString().replace('\n', ' ').replace('\r', ' ')).append('\n');
        }
        return data.toString();
    }

    private String property(String name) {
        try {
            String value = System.getProperty(name);
            if (value == null) return "unavailable";
            if (value.length() > 256) value = value.substring(0, 256) + "...(truncated)";
            return value.replace('\n', ' ').replace('\r', ' ');
        } catch (Exception error) { return "denied: " + error.getClass().getName(); }
    }

    private String field(String message, String name) {
        String prefix = name + "=";
        int start = message.indexOf(prefix);
        if (start < 0 || (start > 0 && message.charAt(start - 1) != '\n')) return "";
        start += prefix.length();
        int end = message.indexOf('\n', start);
        return message.substring(start, end < 0 ? message.length() : end);
    }

    protected void pauseApp() { }
    protected void destroyApp(boolean unconditional) { stopped = true; }
}
