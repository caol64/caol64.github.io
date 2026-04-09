import fs from "node:fs/promises";
import fsSync from "node:fs";
import path from "node:path";
import { argv } from "node:process";
// 宽高比配置
const ASPECT_RATIOS = {
    "1:1": [720, 720],
    "16:9": [1280, 720],
    "9:16": [720, 1280],
    "2.35:1": [900, 383],
};
// 解析命令行参数
function parseArgs() {
    const args = argv.slice(2);
    const prompt = args.find((a) => !a.startsWith("-")) || "";
    const saveIdx = args.indexOf("-s") !== -1 ? args.indexOf("-s") + 1 : -1;
    const ratioIdx = args.indexOf("-r") !== -1 ? args.indexOf("-r") + 1 : -1;
    return {
        prompt,
        save: saveIdx !== -1 ? args[saveIdx] : "result.jpg",
        ratio: ratioIdx !== -1 ? args[ratioIdx] : "16:9",
    };
}
// 下载并保存图片
async function downloadAndSave(url, savePath) {
    const response = await fetch(url);
    const arrayBuffer = await response.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    const dir = path.dirname(savePath);
    if (dir && !fsSync.existsSync(dir)) {
        fsSync.mkdirSync(dir, { recursive: true });
    }
    await fs.writeFile(savePath, buffer);
}
// 主逻辑
async function generateImage(prompt, outputPath, ratio) {
    if (!ASPECT_RATIOS[ratio]) {
        console.log("不支持的比例");
        return;
    }
    // 读取 API Key
    const apiKey = process.env.MODEL_SCOPE_API_KEY;
    if (!apiKey) {
        console.log("错误：未设置 MODEL_SCOPE_API_KEY 环境变量");
        return;
    }
    const [width, height] = ASPECT_RATIOS[ratio];
    const baseUrl = "https://api-inference.modelscope.cn";
    console.log(`正在提交 [${ratio}] 任务 (${width}x${height})...`);
    // 提交生成任务
    const taskRes = await fetch(`${baseUrl}/v1/images/generations`, {
        method: "POST",
        headers: {
            Authorization: `Bearer ${apiKey}`,
            "Content-Type": "application/json",
            "X-ModelScope-Async-Mode": "true",
        },
        body: JSON.stringify({
            model: "Qwen/Qwen-Image-2512",
            prompt,
            negative_prompt: "低分辨率，低画质，肢体畸形，画面过饱和，蜡像感，人脸无细节，过度光滑，画面具有AI感。",
            size: `${width}x${height}`,
        }),
    });
    const task = await taskRes.json();
    const taskId = task.task_id;
    // 轮询查询
    while (true) {
        const resultRes = await fetch(`${baseUrl}/v1/tasks/${taskId}`, {
            headers: {
                Authorization: `Bearer ${apiKey}`,
                "X-ModelScope-Task-Type": "image_generation",
            },
        });
        const result = await resultRes.json();
        const status = result.task_status;
        if (status === "SUCCEED") {
            const imgUrl = result.output_images[0];
            await downloadAndSave(imgUrl, outputPath);
            console.log(`\n✨ 成功！图片已保存至: ${outputPath}`);
            break;
        }
        else if (status === "FAILED") {
            console.log(`\n❌ 失败：${result.message || "未知错误"}`);
            break;
        }
        else {
            process.stdout.write(`\r任务状态: ${status}...`);
        }
        await new Promise((r) => setTimeout(r, 5000));
    }
}
// 启动
const args = parseArgs();
generateImage(args.prompt, args.save, args.ratio);
