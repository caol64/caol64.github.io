const fs = require("fs");
const readline = require("readline");
const path = require("path");

const INPUT_FILE = "../secrets/Comment.0.jsonl";
const OUTPUT_FILE = "../secrets/import_comments.sql";

async function processComments() {
    const fileStream = fs.createReadStream(path.join(__dirname, INPUT_FILE));
    const rl = readline.createInterface({
        input: fileStream,
        crlfDelay: Infinity,
    });

    const writeStream = fs.createWriteStream(path.join(__dirname, OUTPUT_FILE));

    // 写入事务开始
    writeStream.write("BEGIN;\n\n");

    // 映射表：左侧是 SQL 字段名，右侧是处理逻辑
    console.log(`正在处理评论数据...`);

    for await (const line of rl) {
        if (!line.trim() || line.startsWith("#")) continue;

        try {
            const item = JSON.parse(line);

            // 核心逻辑处理
            const row = {
                nick: item.nick || "匿名",
                ip: item.ip || "",
                mail: item.mail || "",
                ua: item.ua || "",
                link: item.link || "",
                comment: item.comment || "",
                url: item.url || "",
                status: item.status || "approved",
                like: item.like || 0,
                // 处理特殊的 Date 对象结构
                insertedAt: item.insertedAt && item.insertedAt.iso ? item.insertedAt.iso : item.createdAt,
                createdAt: item.createdAt,
                updatedAt: item.updatedAt,
                // 先存 objectId 字符串，稍后人工替换
                user_id: item.user_id ?? null,
            };

            const columns = Object.keys(row);
            const values = columns.map((col) => {
                const val = row[col];
                if (val === undefined || val === null) return "NULL";
                // 转义单引号
                const escaped = String(val).replace(/'/g, "''");
                return `'${escaped}'`;
            });

            // 针对 SQL 关键字 like 和 user_id 做引号处理
            const safeColumns = columns.map((c) => (c === "like" ? '"like"' : c));

            const sql = `INSERT INTO wl_comment (${safeColumns.join(", ")}) VALUES (${values.join(", ")});\n`;
            writeStream.write(sql);
        } catch (e) {
            console.error(`解析失败: ${e.message}`);
        }
    }

    writeStream.write("\nCOMMIT;");
    writeStream.end();
    console.log(`处理完成！SQL 已生成至: ${OUTPUT_FILE}`);
}

processComments();
