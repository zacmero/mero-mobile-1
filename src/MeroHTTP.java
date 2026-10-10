import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import javax.microedition.io.Connector;
import javax.microedition.io.HttpConnection;
import javax.microedition.io.StreamConnection;
import javax.microedition.lcdui.Canvas;
import javax.microedition.lcdui.Command;
import javax.microedition.lcdui.CommandListener;
import javax.microedition.lcdui.Display;
import javax.microedition.lcdui.Displayable;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Form;
import javax.microedition.midlet.MIDlet;

public final class MeroHTTP extends MIDlet implements CommandListener, Runnable {
    private Screen screen;
    private volatile String status = "Starting";
    private volatile boolean stopping;
    private volatile boolean paused;
    private volatile boolean running;
    private volatile int transport = 2;
    private boolean restartRequested;
    private String requestMethod = "GET";
    private String stage = "startup";
    private volatile HttpConnection connection;
    private volatile StreamConnection socketConnection;
    private volatile int lastKey;
    private int sequence;
    private String ack = "none";
    private String result = "startup";
    private Command connect = new Command("Connect", Command.SCREEN, 1);
    private Command stop = new Command("Stop", Command.SCREEN, 2);
    private Command exit = new Command("Exit", Command.EXIT, 3);
    private Command mode = new Command("GET/POST/TCP", Command.SCREEN, 4);
    private Command details = new Command("Details", Command.SCREEN, 5);
    private Command back = new Command("Back", Command.BACK, 1);

    protected void startApp() {
        paused = false;
        if (screen == null) {
            screen = new Screen();
            screen.addCommand(connect);
            screen.addCommand(stop);
            screen.addCommand(exit);
            screen.addCommand(mode);
            screen.addCommand(details);
            screen.setCommandListener(this);
            Display.getDisplay(this).setCurrent(screen);
            startConnection();
        } else Display.getDisplay(this).setCurrent(screen);
    }

    private synchronized void startConnection() {
        if (running) {
            if (stopping) restartRequested = true;
            return;
        }
        stopping = false;
        running = true;
        new Thread(this).start();
    }

    private void report(String text) { status = text; screen.repaint(); }

    public void run() {
        try {
            while (!stopping) {
                if (!paused) {
                    try {
                        report("Connecting to computer");
                        String response = exchange();
                        String id = field(response, "command_id");
                        String command = field(response, "command");
                        if (id.length() == 0 || command.length() == 0) throw new java.io.IOException("Invalid server reply");
                        if (id.length() > 0 && !id.equals(ack)) {
                            if (command.equals("PING")) result = "PONG";
                            else if (command.equals("INFO") || command.equals("HEAP") || command.equals("SCREEN")
                                || command.equals("KEY") || command.equals("CAPABILITIES")) result = command + " OK";
                            else result = "Unknown command";
                            ack = id;
                        }
                        report("Connected. Upload " + sequence + "\n" + result);
                    } catch (Exception error) {
                        if (!stopping) report(requestMethod + " failed at " + stage + "\n" + error.toString());
                    } finally {
                        try { if (connection != null) connection.close(); } catch (Exception error) { }
                        try { if (socketConnection != null) socketConnection.close(); } catch (Exception error) { }
                        connection = null;
                        socketConnection = null;
                    }
                }
                try { Thread.sleep(2000); } catch (Exception error) { }
            }
        } finally {
            synchronized (this) {
                running = false;
                if (restartRequested) { restartRequested = false; startConnection(); }
            }
        }
    }

    private String exchange() throws Exception {
        stage = "prepare diagnostics";
        int selected = transport;
        boolean post = selected == 1;
        requestMethod = selected == 2 ? "TCP" : post ? "POST" : "GET";
        byte[] bytes = info().getBytes("UTF-8");
        if (selected == 2) return socketExchange(bytes);
        stage = "open connection";
        String url = post ? HTTPSettings.URL : HTTPSettings.URL + "?data=" + encode(bytes);
        connection = (HttpConnection) Connector.open(url);
        stage = "request headers";
        connection.setRequestMethod(post ? HttpConnection.POST : HttpConnection.GET);
        if (post) {
            connection.setRequestProperty("Content-Type", "text/plain; charset=utf-8");
            connection.setRequestProperty("Content-Length", String.valueOf(bytes.length));
            stage = "open output";
            OutputStream output = connection.openOutputStream();
            try { stage = "write body"; output.write(bytes); output.flush(); }
            finally { stage = "close output"; output.close(); }
        }
        stage = "response status";
        int code = connection.getResponseCode();
        if (code != HttpConnection.HTTP_OK) throw new java.io.IOException("HTTP status " + code);
        stage = "read response";
        InputStream input = connection.openInputStream();
        ByteArrayOutputStream reply = new ByteArrayOutputStream();
        try {
            int c;
            while ((c = input.read()) != -1) {
                if (reply.size() >= 4096) throw new java.io.IOException("Response too large");
                reply.write(c);
            }
        } finally { input.close(); }
        return new String(reply.toByteArray(), "UTF-8");
    }

    private String socketExchange(byte[] bytes) throws Exception {
        String url = HTTPSettings.URL.substring(7);
        int slash = url.indexOf('/');
        String host = url.substring(0, slash);
        String path = url.substring(slash) + "?data=" + encode(bytes);
        stage = "open TCP socket";
        socketConnection = (StreamConnection) Connector.open("socket://" + host);
        stage = "write TCP request";
        OutputStream output = socketConnection.openOutputStream();
        output.write(("GET " + path + " HTTP/1.0\r\nHost: " + host
            + "\r\nUser-Agent: MeroHTTP-TCP/0.3\r\nConnection: close\r\n\r\n").getBytes("UTF-8"));
        output.flush();
        stage = "read TCP response";
        InputStream input = socketConnection.openInputStream();
        ByteArrayOutputStream reply = new ByteArrayOutputStream();
        try {
            int c;
            while ((c = input.read()) != -1) {
                if (reply.size() >= 8192) throw new java.io.IOException("TCP reply too large");
                reply.write(c);
            }
        } finally { input.close(); output.close(); }
        String response = new String(reply.toByteArray(), "UTF-8");
        int headers = response.indexOf("\r\n\r\n");
        int line = response.indexOf("\r\n");
        if (headers < 0 || line < 0 || response.substring(0, line).indexOf(" 200 ") < 0)
            throw new java.io.IOException("Invalid TCP HTTP response");
        return response.substring(headers + 4);
    }

    private String encode(byte[] bytes) {
        String hex = "0123456789ABCDEF";
        StringBuffer encoded = new StringBuffer();
        for (int i = 0; i < bytes.length; i++) {
            int c = bytes[i] & 255;
            if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9')
                || c == '-' || c == '_' || c == '.') encoded.append((char) c);
            else { encoded.append('%'); encoded.append(hex.charAt(c >> 4)); encoded.append(hex.charAt(c & 15)); }
        }
        return encoded.toString();
    }

    private String info() {
        Runtime vm = Runtime.getRuntime();
        sequence++;
        return "protocol=mero-http/1\ntransport=" + requestMethod + "\nseq=" + sequence + "\nack=" + ack + "\nresult=" + result
            + "\nconfig=" + property("microedition.configuration")
            + "\nprofiles=" + property("microedition.profiles")
            + "\nplatform=" + property("microedition.platform")
            + "\nlocale=" + property("microedition.locale")
            + "\nheap_free=" + vm.freeMemory() + "\nheap_total=" + vm.totalMemory()
            + "\nwidth=" + screen.getWidth() + "\nheight=" + screen.getHeight()
            + "\ncolors=" + Display.getDisplay(this).numColors()
            + "\nkey=" + lastKey
            + "\njsr75=" + available("javax.microedition.io.file.FileConnection")
            + "\njsr135=" + available("javax.microedition.media.Manager")
            + "\njsr82=" + available("javax.bluetooth.LocalDevice")
            + "\nfileconnection_version=" + property("microedition.io.file.FileConnection.version")
            + "\nmedia_version=" + property("microedition.media.version") + "\n";
    }

    private String property(String name) {
        String value = System.getProperty(name);
        if (value == null) return "unknown";
        StringBuffer safe = new StringBuffer();
        for (int i = 0; i < value.length(); i++) {
            char c = value.charAt(i);
            safe.append(c == '\n' || c == '\r' ? ' ' : c);
        }
        return safe.toString();
    }

    private boolean available(String name) {
        try { Class.forName(name); return true; }
        catch (Throwable error) { return false; }
    }

    private String field(String response, String name) {
        String prefix = name + "=";
        int start = response.indexOf(prefix);
        if (start < 0 || (start > 0 && response.charAt(start - 1) != '\n')) return "";
        start += prefix.length();
        int end = response.indexOf('\n', start);
        return response.substring(start, end < 0 ? response.length() : end);
    }

    public void commandAction(Command command, Displayable displayable) {
        if (command == connect) startConnection();
        else if (command == mode) { transport = (transport + 1) % 3; report(transport == 2 ? "TCP selected" : transport == 1 ? "POST selected" : "GET selected"); startConnection(); }
        else if (command == details) {
            Form form = new Form("Local diagnostics");
            form.append(info());
            form.addCommand(back);
            form.setCommandListener(this);
            Display.getDisplay(this).setCurrent(form);
        }
        else if (command == back) Display.getDisplay(this).setCurrent(screen);
        else if (command == stop) { stopConnection(); report("Stopped"); }
        else if (command == exit) { destroyApp(true); notifyDestroyed(); }
    }

    private synchronized void stopConnection() {
        stopping = true;
        restartRequested = false;
        try { if (connection != null) connection.close(); } catch (Exception error) { }
        try { if (socketConnection != null) socketConnection.close(); } catch (Exception error) { }
    }

    protected void pauseApp() { paused = true; }
    protected void destroyApp(boolean unconditional) { stopConnection(); }

    private final class Screen extends Canvas {
        protected void paint(Graphics g) {
            g.setColor(0xffffff);
            g.fillRect(0, 0, getWidth(), getHeight());
            g.setColor(0);
            int h = g.getFont().getHeight();
            g.drawString("MERO HTTP v0.3", 2, 2, Graphics.TOP | Graphics.LEFT);
            String text = status;
            int start = 0;
            int row = 1;
            while (start < text.length()) {
                int end = start;
                while (end < text.length() && text.charAt(end) != '\n'
                    && g.getFont().substringWidth(text, start, end - start + 1) < getWidth() - 4) end++;
                if (end == start && text.charAt(end) != '\n') end++;
                g.drawString(text.substring(start, end), 2, 2 + row * h, Graphics.TOP | Graphics.LEFT);
                start = end < text.length() && text.charAt(end) == '\n' ? end + 1 : end;
                row++;
            }
            g.drawString("Key: " + lastKey, 2, 2 + row * h, Graphics.TOP | Graphics.LEFT);
        }
        protected void keyPressed(int code) { lastKey = code; repaint(); }
    }
}
