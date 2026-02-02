const fs = require("fs");
const readline = require("readline");
const path = require("path");

// 配置：你的源文件名和输出 SQL 文件名
const INPUT_FILE = "../secrets/Users.0.jsonl";
const OUTPUT_FILE = "../secrets/import_users.sql";

async function processFile() {
    const fileStream = fs.createReadStream(path.join(__dirname, INPUT_FILE));
    const rl = readline.createInterface({
        input: fileStream,
        crlfDelay: Infinity,
    });

    const writeStream = fs.createWriteStream(path.join(__dirname, OUTPUT_FILE));

    // SQL 定义中的字段映射
    const columns = [
        "display_name",
        "email",
        "password",
        "type",
        "url",
        "avatar",
        "github",
        "createdAt",
        "updatedAt",
        '"2fa"',
    ];

    console.log(`正在处理文件: ${INPUT_FILE} ...`);

    for await (const line of rl) {
        // 跳过空行或非 JSON 行
        if (!line.trim() || line.startsWith("#")) continue;

        try {
            const item = JSON.parse(line);

            const values = columns.map((col) => {
                const key = col.replace(/"/g, ""); // 移除 "2fa" 的引号来匹配 JSON 键
                const val = item[key];

                // 处理空值
                if (val === undefined || val === null || val === "") {
                    // 必须填写的字段给空字符串，其他给 NULL
                    if (["display_name", "email", "password", "type"].includes(key)) return "''";
                    return "NULL";
                }

                // 转义单引号并包裹
                const escapedVal = String(val).replace(/'/g, "''");
                return `'${escapedVal}'`;
            });

            const sql = `INSERT INTO wl_users (${columns.join(", ")}) VALUES (${values.join(", ")});\n`;
            writeStream.write(sql);
        } catch (e) {
            console.error(`解析行失败: ${line.substring(0, 50)}... 错误: ${e.message}`);
        }
    }

    writeStream.end();
    console.log(`处理完成！SQL 已生成至: ${OUTPUT_FILE}`);
}

processFile();
