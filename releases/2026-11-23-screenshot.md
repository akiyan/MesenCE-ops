# 2026-11-23 負荷に左右されないスクリーンショット

| 項目 | 値 |
|---|---|
| 上流基準 | `20ba206cef5ba207c21203176d02cb9f43dda9fb` |
| 独自コミット | `b7e031867a5b0630c24da865b144716a3bd64c99` |
| 再取得用タグ | `akiyan-2026-11-23-screenshot` |
| 実行環境 | Linux x86-64、GCC、SDL2（20 コア） |

直前の版は `akiyan-2026-11-22-capture` で取得できる。 [本体の変更](https://github.com/akiyan/MesenCE/commit/b7e031867a5b0630c24da865b144716a3bd64c99) · [Issue #10](https://github.com/akiyan/MesenCE/issues/10) · [再実行手順](../docs/setup.md)

Lua の `emu.takeScreenshot()` が、デコーダーに渡した最後のフレームの変換の終わりを待つようにした（`VideoDecoder::WaitForAsyncFrameDecode()`。済んでいれば待たない）。
`endFrame` での PNG は、負荷に関係なく常に 1 つ前のフレームになる。負荷のないときの結果と同じなので、既存のスクリプトのフレームの対応は変わらない。

| 確認 | 結果 |
|---|---|
| `tests/headless_screenshot.py`（新設） | ゲームギアの自作 ROM（背景が毎フレーム赤と青で交互）を、コアあたり 2 個の空回りのプロセス（40 個）と同時に動かし、`endFrame` の PNG 599 枚がすべて 1 つ前のフレームの色。3 回とも通過 |
| 同じ試験を直前の版で | 599 枚中 24 枚が 2 つ前のフレーム（失敗） |
| 直前の版の 300 フレームの観測 | 負荷なしで 300 枚すべて 1 つ前。負荷 15 前後で 300 枚中 6 枚、17 枚が 2 つ前 |
| 従来の試験 | 全て通過 |
| 利用側（kamaitachi-ops）の確認 | ゲームギア版の選択肢のカーソル（毎フレームの PNG）が通過 |
