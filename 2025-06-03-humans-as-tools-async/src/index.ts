import { cli } from "./cli"

async function main() {
    await cli()
}

main().catch(console.error)