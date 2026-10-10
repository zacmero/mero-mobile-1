import javax.microedition.midlet.MIDlet;
import javax.microedition.lcdui.Canvas;
import javax.microedition.lcdui.Command;
import javax.microedition.lcdui.CommandListener;
import javax.microedition.lcdui.Display;
import javax.microedition.lcdui.Displayable;
import javax.microedition.lcdui.Graphics;
import javax.microedition.io.Connection;

public final class MeroLink extends MIDlet implements CommandListener {
    public static volatile boolean stopping;
    public static Connection listener;
    public static Connection peer;
    private static LinkScreen screen;
    private static String status = "Starting";
    private static int lastKey;
    private Command exit = new Command("Exit", Command.EXIT, 1);

    protected void startApp() {
        if (screen == null) {
            stopping = false;
            screen = new LinkScreen();
            screen.addCommand(exit);
            screen.setCommandListener(this);
            Display.getDisplay(this).setCurrent(screen);
            try {
                Class.forName("javax.bluetooth.LocalDevice");
                Runnable link = (Runnable) Class.forName("BluetoothLink").newInstance();
                new Thread(link).start();
            } catch (Throwable error) {
                report("Bluetooth unavailable: " + error.toString());
            }
        } else {
            Display.getDisplay(this).setCurrent(screen);
        }
    }

    public static void report(String message) {
        status = message;
        if (screen != null) screen.repaint();
    }

    public static String info() {
        Runtime vm = Runtime.getRuntime();
        return "config=" + System.getProperty("microedition.configuration")
            + "\nprofiles=" + System.getProperty("microedition.profiles")
            + "\nplatform=" + System.getProperty("microedition.platform")
            + "\nlocale=" + System.getProperty("microedition.locale")
            + "\nheap_free=" + vm.freeMemory() + "\nheap_total=" + vm.totalMemory()
            + "\nwidth=" + screen.getWidth() + "\nheight=" + screen.getHeight()
            + "\ncolors=" + Display.getDisplay(screen.owner).numColors()
            + "\nkey=" + lastKey
            + "\njsr75=" + available("javax.microedition.io.file.FileConnection")
            + "\njsr135=" + available("javax.microedition.media.Manager")
            + "\njsr82=" + available("javax.bluetooth.LocalDevice");
    }

    private static boolean available(String name) {
        try { Class.forName(name); return true; }
        catch (Throwable error) { return false; }
    }

    public void commandAction(Command command, Displayable displayable) {
        if (command == exit) {
            destroyApp(true);
            notifyDestroyed();
        }
    }

    protected void pauseApp() { }

    protected void destroyApp(boolean unconditional) {
        stopping = true;
        try { if (peer != null) peer.close(); } catch (Exception error) { }
        try { if (listener != null) listener.close(); } catch (Exception error) { }
    }

    private final class LinkScreen extends Canvas {
        private MeroLink owner = MeroLink.this;
        protected void paint(Graphics g) {
            g.setColor(0xffffff);
            g.fillRect(0, 0, getWidth(), getHeight());
            g.setColor(0);
            int h = g.getFont().getHeight();
            g.drawString("MERO BLUETOOTH LINK", 2, 2, Graphics.TOP | Graphics.LEFT);
            // Wrap status text so errors remain readable on a small display.
            int row = 1;
            int start = 0;
            while (start < status.length()) {
                int end = start + 1;
                while (end < status.length() && g.getFont().substringWidth(status, start, end - start + 1) < getWidth() - 4) end++;
                g.drawString(status.substring(start, end), 2, 2 + row * h, Graphics.TOP | Graphics.LEFT);
                start = end;
                row++;
            }
            g.drawString("Key: " + lastKey, 2, 2 + row * h, Graphics.TOP | Graphics.LEFT);
        }
        protected void keyPressed(int code) { lastKey = code; repaint(); }
    }
}
