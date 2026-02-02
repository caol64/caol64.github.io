const fs = require("fs");
const readline = require("readline");
const path = require("path");

// 配置输入输出文件名
const INPUT_FILE = "../secrets/Comment.0.jsonl";
const OUTPUT_FILE = "../secrets/pid_rid_map.json";

async function extractIds() {
    const inputPath = path.join(__dirname, INPUT_FILE);
    const outputPath = path.join(__dirname, OUTPUT_FILE);

    if (!fs.existsSync(inputPath)) {
        console.error(`错误：找不到文件 ${INPUT_FILE}`);
        return;
    }

    const fileStream = fs.createReadStream(inputPath);
    const rl = readline.createInterface({
        input: fileStream,
        crlfDelay: Infinity,
    });

    const outputStream = fs.createWriteStream(outputPath);

    console.log(`正在处理 ${INPUT_FILE} ...`);

    for await (const line of rl) {
        // 仅处理 JSON 行
        if (line.trim().startsWith("{")) {
            try {
                const data = JSON.parse(line);

                // 构造只包含 ID 关联的新对象
                const simplified = {
                    objectId: data.objectId || null, // 当前评论的旧 ID
                    pid: data.pid || null, // 父评论旧 ID
                    rid: data.rid || null, // 根评论旧 ID
                };

                outputStream.write(JSON.stringify(simplified) + "\n");
            } catch (err) {
                console.error(`解析行失败，已跳过: ${line.substring(0, 50)}...`);
            }
        }
    }

    outputStream.end();
    console.log(`✅ 提取完成！结果已保存至: ${OUTPUT_FILE}`);
}

extractIds();
