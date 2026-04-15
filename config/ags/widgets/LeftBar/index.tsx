import { Astal, Gdk, Gtk } from "ags/gtk4"
import app from "ags/gtk4/app"
import { onCleanup } from "ags"

import { Date } from "./components/Date"

const { CENTER } = Gtk.Align
const { TOP, BOTTOM, LEFT, RIGHT } = Astal.WindowAnchor
const { EXCLUSIVE } = Astal.Exclusivity
// const { transparent, position } = options.bar
import style from "./style.scss"

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
      name="left-bar"
      visible
      class="left-bar"
      css={style}
      gdkmonitor={gdkmonitor}
      exclusivity={EXCLUSIVE}
      anchor={LEFT|TOP|BOTTOM}
      application={app}
    >
      <centerbox valign={CENTER}>
        <box $type="center" class="vertical" valign={CENTER}>
          <Date.TimeObject />
        </box>
      </centerbox>
    </window >
  )
}

