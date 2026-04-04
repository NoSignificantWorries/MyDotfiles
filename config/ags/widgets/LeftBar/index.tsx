import { Astal, Gdk, Gtk } from "ags/gtk4"
import app from "ags/gtk4/app"
import { onCleanup } from "ags"

import { Date } from "./components/Date"

const { CENTER } = Gtk.Align
const { TOP, BOTTOM, LEFT, RIGHT } = Astal.WindowAnchor
const { EXCLUSIVE } = Astal.Exclusivity
// const { transparent, position } = options.bar

export function LeftBar({ gdkmonitor }: { gdkmonitor: Gdk.Monitor }) {
  let win: Astal.Window

  onCleanup(() => {
    win.destroy()
  })

  return (
    <window
      $={self => {
        win = self
      }}
      name="bar"
      visible
      class="bar"
      gdkmonitor={gdkmonitor}
      exclusivity={EXCLUSIVE}
      anchor={LEFT|TOP|BOTTOM}
      application={app}
    >
      <centerbox valign={CENTER}>
        <box $type="center" class="horizontal" valign={CENTER}>
          <Date.TimeObject />
        </box>
      </centerbox>
    </window >
  )
}

