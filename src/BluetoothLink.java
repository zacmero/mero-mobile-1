import java.io.InputStream;
import java.io.OutputStream;
import javax.bluetooth.DiscoveryAgent;
import javax.bluetooth.LocalDevice;
import javax.microedition.io.Connector;
import javax.microedition.io.StreamConnection;
import javax.microedition.io.StreamConnectionNotifier;

// Loaded reflectively by MeroLink; absent JSR-82 is reported by the main MIDlet.
public final class BluetoothLink implements Runnable {
    public void run() {
        StreamConnectionNotifier server = null;
        try {
            LocalDevice local = LocalDevice.getLocalDevice();
            local.setDiscoverable(DiscoveryAgent.GIAC);
            server = (StreamConnectionNotifier) Connector.open(
                "btspp://localhost:7ca9012e6d154802a320a1b2c3d4e501;name=MeroLink;authenticate=true;encrypt=true");
            MeroLink.listener = server;
            while (!MeroLink.stopping) {
                MeroLink.report("JSR82 available. Waiting for computer.");
                StreamConnection connection = server.acceptAndOpen();
                MeroLink.peer = connection;
                try {
                    MeroLink.report("Computer connected");
                    InputStream in = connection.openInputStream();
                    OutputStream out = connection.openOutputStream();
                    reply(out, "MERO-LINK/1\n" + MeroLink.info());
                    StringBuffer line = new StringBuffer();
                    int c;
                    while (!MeroLink.stopping && (c = in.read()) != -1) {
                        if (c == '\n') {
                            String command = line.toString();
                            line.setLength(0);
                            if (command.equals("PING")) reply(out, "PONG");
                            else if (command.equals("INFO") || command.equals("HEAP") || command.equals("SCREEN") || command.equals("KEY")) reply(out, MeroLink.info());
                            else if (command.equals("BYE")) { reply(out, "BYE"); break; }
                            else reply(out, "ERROR unknown command");
                        } else if (c != '\r') {
                            if (line.length() >= 64) { reply(out, "ERROR command too long"); break; }
                            line.append((char) c);
                        }
                    }
                } catch (Exception error) {
                    if (!MeroLink.stopping) MeroLink.report("Peer error: " + error.toString());
                } finally {
                    connection.close();
                    MeroLink.peer = null;
                }
            }
        } catch (Throwable error) {
            if (!MeroLink.stopping) MeroLink.report("Bluetooth error: " + error.toString());
        } finally {
            try { if (server != null) server.close(); } catch (Exception error) { }
            MeroLink.listener = null;
        }
    }

    private void reply(OutputStream out, String message) throws java.io.IOException {
        out.write((message + "\nEND\n").getBytes("UTF-8"));
        out.flush();
    }
}
