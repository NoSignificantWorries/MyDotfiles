#!/usr/bin/env -S ags run

import env from "$lib/env"

import app from "ags/gtk4/app"
import { createBinding, For, This } from "ags"

import { LeftBar } from "./widgets/LeftBar"
import { default as HudTest } from "./widgets/HudTest"


app.start({
  instanceName: env.appName,
  main() {
    const monitors = createBinding(app, "monitors");

    app.add_window(HudTest());

    // return (
    //   <For each={monitors}>
    //     {(monitor) => (
    //       <This this={app}>
    //         <LeftBar gdkmonitor={monitor} />
    //       </This>
    //     )}
    //   </For>
    // )
  }
})

