// Educational Java ME / MIDP example.
// UNTESTED: build only after identifying the phone's Java platform.
// No Java SE features or optional JSR APIs required.
import javax.microedition.midlet.MIDlet;
import javax.microedition.lcdui.Command;
import javax.microedition.lcdui.CommandListener;
import javax.microedition.lcdui.Display;
import javax.microedition.lcdui.Displayable;
import javax.microedition.lcdui.Form;

public final class MeroHello extends MIDlet implements CommandListener {
    private Form screen;
    private Command refreshCommand;
    private Command exitCommand;

    protected void startApp() {
        if (screen == null) {
            screen = new Form("MERO HELLO");
            refreshCommand = new Command("Refresh", Command.SCREEN, 1);
            exitCommand = new Command("Exit", Command.EXIT, 2);
            screen.addCommand(refreshCommand);
            screen.addCommand(exitCommand);
            screen.setCommandListener(this);
        }

        refresh();
        Display.getDisplay(this).setCurrent(screen);
    }

    private void refresh() {
        screen.deleteAll();
        screen.append("Mero Mobile #1\n");
        screen.append("Java ME field probe\n\n");
        appendProperty("Config", "microedition.configuration");
        appendProperty("Profiles", "microedition.profiles");
        appendProperty("Platform", "microedition.platform");
        appendProperty("Locale", "microedition.locale");

        Runtime vm = Runtime.getRuntime();
        screen.append("\nHeap free: " + vm.freeMemory() + "\n");
        screen.append("Heap total: " + vm.totalMemory() + "\n");
        screen.append("\nPress Refresh or Exit.");
    }

    private void appendProperty(String title, String name) {
        String value = System.getProperty(name);
        screen.append(title + ": " + (value == null ? "unknown" : value) + "\n");
    }

    public void commandAction(Command command, Displayable displayable) {
        if (command == exitCommand) {
            notifyDestroyed();
        } else if (command == refreshCommand) {
            refresh();
        }
    }

    protected void pauseApp() {
        // No background resources in this small example.
    }

    protected void destroyApp(boolean unconditional) {
        // Nothing to release yet.
    }
}
