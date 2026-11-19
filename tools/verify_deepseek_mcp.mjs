// Run using the installed DeepSeek Harness Electron executable in Node mode.
import { pathToFileURL } from 'node:url';

const [modules, command] = process.argv.slice(2);
if (!modules || !command) throw new Error('Expected DSH node_modules and MCP command');
const load = (name) => import(pathToFileURL(`${modules}/@deepseek-ai/${name}/lib/index.js`).href);
const { Context } = await load('cordis');
const toolsModule = await load('dsh-tools');
const promptModule = await load('dsh-system-prompt');
const mcp = await load('dsh-mcp-client');
const ctx = new Context();
const deadline = setTimeout(() => { console.error('DSH MCP verification timed out'); process.exit(1); }, 30000);
try {
    ctx.plugin(promptModule.default ?? promptModule);
    ctx.plugin(toolsModule.default);
    const connection = ctx.plugin(mcp, {
        serverName: 'ddl-reminder', transport: 'stdio', command, args: [],
        failOnStartupError: true,
    });
    await connection.await();
    const name = 'mcp__ddl-reminder__get_local_time';
    let names = [];
    for (let attempt = 0; attempt < 150; attempt++) {
        names = ctx.tools.schemas().map(tool => tool.name);
        if (names.includes(name)) break;
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    if (!names.includes(name)) throw new Error('DSH did not discover DDL Reminder tools');
    const definition = ctx.tools.get(name);
    const result = await definition.execute({}, { signal: new AbortController().signal });
    console.log(JSON.stringify({client: 'DeepSeek Harness', tools: names, result}));
} catch (error) {
    console.error(error);
    process.exitCode = 1;
} finally {
    clearTimeout(deadline);
    await Promise.race([ctx.fiber.dispose(), new Promise(resolve => setTimeout(resolve, 3000))]);
    process.exit(process.exitCode ?? 0);
}
