import env from "$lib/env"


export namespace Date {
  export function TimeObject() {
    return (
      <label class="clock" label={env.clock(v => v.format("%H:%M") ?? "")}/>
    )
  }
}

