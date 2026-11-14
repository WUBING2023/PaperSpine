# PaperSpine 安装说明

| 下载版本 | 使用方式 |
| --- | --- |
| 全流程 Skill | `$paper-spine`。在对话里给出题目、已有结果或稿件，完成适用的研究、写作、制图、审阅与交付。 |
| Skills 包 | `$paper-spine`，或单独调用 `$paper-spine-study`、`$paper-spine-followwriting`、`$paper-spine-figures`、`$paper-spine-review`、`$paper-spine-deliver`。 |
| Web 插件包 | 安装完整 Skills 包和可选工作台入口。Windows x64 Codex 用户可选 PaperSpine Web 技能（`$paper-spine-web:paper-spine-web`）来配置论文、比较图件、预览、下载和提交反馈。 |

## 安装

从下载页选择一个 ZIP，并下载 `checksums.sha256`。解压 ZIP，在解压目录运行下列命令。将 `<ZIP>` 替换为原 ZIP 路径，`<SHA256>` 替换为校验文件中所选版本对应的完整散列值。

```text
python -B edition_manager.py install "<ZIP>" --sha256 <SHA256>
```

管理器需要 Python 3.12 或更新版。默认安装到当前 Codex 用户的 `skills` 目录。Web 版另需 `codex` CLI，解压后可以用 `runtime\runtime_vendor\windows-py312\python.exe` 运行安装器。只用 Skill 的其他宿主可以在 `install` 前传入 `--skills-root <宿主的Skill目录>`，也可以把 ZIP 的 `skills/` 下各目录直接放在宿主的 Skill 目录同一级。打开新对话后确认入口可用。生成 Word、PDF 或图表所需的工具随任务和宿主能力而定。

如果 `paper-spine` 目录已有旧版，安装器会保留现有内容并提示。明确要在同一宿主换版时，可用 `--archive-existing` 将旧 `paper-spine` 整目录移出发现路径。卸载时会恢复这份旧入口。其他同名 Skill 冲突会报告具体目录。工作台默认把任务保存在独立 profile，命令结果会显示位置；可以用 `--profile-root` 指定独立目录。旧版任务应先确认原 profile 和运行时绑定，旧 profile 的无缝迁移还需验证。

## 更新与卸载

安装完成后，用命令输出的 `manager` 路径运行以下命令。安装时用过 `--skills-root` 就在子命令前传同一个目录。

```text
python -B "<manager>" status
python -B "<manager>" check
python -B "<manager>" update
python -B "<manager>" auto-update off
python -B "<manager>" auto-update on
python -B "<manager>" rollback
python -B "<manager>" uninstall
```

公开发行包安装后使用内置 V6 更新频道。离线包或测试包可在安装命令后加 `--channel "<channel.json>"` 指定本地频道。新一次调用会间隔检查更新。当前版本形态整组更新，校验频道内的字节数、SHA-256 和包内文件清单，并保留一个可回退版本。离线时继续使用已安装方法。自动检查遇到仍打开的工作台会暂缓，保存工作后可用 `web stop` 再更新。回退、手动换版后打开一个新对话，让宿主重新发现 Skills。

卸载移除 managed Skills 和 Web 插件（如果已装），保留 `profile_root` 中的论文任务和配置。用户自己的研究资料和导出目录独立保留。直接手动复制的安装可以移出当初复制的目录。
