// import { App, Widget, Gtk, Gdk } from "astal/gtk4";
import { Astal, Widget, Gdk, Gtk } from "ags/gtk4"
import Hyprland from "gi://AstalHyprland";

const hypr = Hyprland.get_default();

// Функция для получения текущего активного окна
const getActiveClient = () => {
    return hypr.focusedClient;
};

// Виджет с информацией
const ActiveWindowLabel = () => {
    // Связываем (bind) текст метки с заголовком активного окна
    // Если окно не сфокусировано, показываем "Desktop"
    return (
        <label
            cssClasses={["window-title"]}
            halign={Gtk.Align.CENTER}
            valign={Gtk.Align.CENTER}
            label={hypr.focusedClient.bind("title").as(t => t || "Desktop")}
        />
    );
};

// Функция для обновления позиции окна
const updatePosition = (window) => {
    const client = getActiveClient();
    if (!client) {
        window.visible = false;
        return;
    }

    window.visible = true;
    
    // Получаем геометрию активного окна
    const geo = client.get_geometry();
    
    // Устанавливаем позицию виджета (например, над заголовком окна)
    // X: центр окна минус половина ширины виджета
    // Y: верхняя граница окна + небольшой отступ (чтобы не перекрывать заголовок)
    const widgetWidth = 200;
    const offsetY = 5;
    
    window.set_position(
        Gtk.WindowPosition.NONE // Отключаем автоматическое позиционирование
    );
    
    // Перемещаем окно (это работает для обычных Gtk окон в X11/Wayland)
    window.default_width = widgetWidth;
    window.default_height = 50;
    
    // Используем move для установки позиции (требует реализации через GdkSurface)
    // Более надежный способ - задать гравитацию окна и координаты относительно монитора
    const monitor = hypr.get_monitor(client.monitor);
    if (monitor) {
        window.set_transient_for(client.get_gdk_window()); // Привязка к окну (может не работать в Wayland)
    }
};

export default () => {
    const window = (
        <window
            name="active-window-info"
            namespace="ags-window-info"
            // application={App}
            cssClasses={["window-info"]}
            visible={false}
            keymode={Gtk.Keymode.NONE} // Игнорируем ввод, окно некликабельное
            layer={Gtk.Layer.OVERLAY} // Показываем поверх всех окон
            anchor={Gtk.Anchor.TOP | Gtk.Anchor.LEFT} // Привязываем к левому верхнему углу
            exclusivity={Gtk.Exclusivity.IGNORE} // Не резервируем место на экране
            focusable={false} // Окно не может получать фокус
            // Настройки для Wayland (Hyprland)
            on_realize={(self) => {
                // Делаем окно плавающим (float) и снимаем декорации
                const gdkWin = self.get_native();
                if (gdkWin) {
                    gdkWin.set_decorations(Gdk.WMDecoration.NONE);
                }
            }}
        >
            <box cssClasses={["container"]} spacing={10}>
                <image iconName="window-duplicate-symbolic" />
                <ActiveWindowLabel />
            </box>
        </window>
    );

    // Подписываемся на смену активного окна
    hypr.connect("notify::focused-client", () => {
        updatePosition(window);
    });

    // Подписываемся на движение/изменение размера активного окна
    hypr.connect("client-moved", (_, client) => {
        if (client === getActiveClient()) {
            updatePosition(window);
        }
    });

    hypr.connect("client-resized", (_, client) => {
        if (client === getActiveClient()) {
            updatePosition(window);
        }
    });

    // Инициализация при старте
    // App.connect("window-initialized", () => {
    //     updatePosition(window);
    // });

    return window;
};

