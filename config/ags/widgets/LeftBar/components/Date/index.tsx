import env from "$lib/env"


import style from "./style.scss"


export namespace Date {
  export function TimeObject() {
    return (
      <label class="clock" css={style} label={env.clock(v => v.format("%H:%M") ?? "")}/>
    )
  }
}

