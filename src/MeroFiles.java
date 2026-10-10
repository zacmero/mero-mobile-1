import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.Enumeration;
import javax.microedition.io.Connector;
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

    protected void startApp() {
        if (roots == null) {
            roots = new List("MERO FILES v0.4 - storage", List.IMPLICIT);
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
        status = new Form("MERO FILES v0.4");
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
                            && (command.equals("PING") || command.equals("INFO"))) {
                        commandStatus = "accepted " + command;
                        ack = id;
                        result = command.equals("PING") ? "PONG" : "INFO OK";
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
            if (size > 4096) return null;
            InputStream input = file.openInputStream();
            try {
                ByteArrayOutputStream bytes = new ByteArrayOutputStream();
                int c;
                while ((c = input.read()) != -1) {
                    if (bytes.size() >= 4096) return null;
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
            + "\nmedia_version=" + property("microedition.media.version") + "\nend=1\n";
    }

    private String property(String name) {
        String value = System.getProperty(name);
        if (value == null) return "unavailable";
        return value.replace('\n', ' ').replace('\r', ' ');
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
