# 2026-11-22 マスターシステム・ゲームギアのフレーム数の修正

| 項目 | 値 |
|---|---|
| 上流基準 | `20ba206cef5ba207c21203176d02cb9f43dda9fb` |
| 独自コミット | `ba2f85e90b92001c7f2f1244b32ed083dbb4cb0c` |
| 再取得用タグ | `akiyan-2026-11-22-frame-count` |
| 実行環境 | Linux x86-64、GCC、SDL2 |

直前の版は `akiyan-2026-11-22-game-gear-audio` で取得できる。 [本体の変更](https://github.com/akiyan/MesenCE/commit/ba2f85e90b92001c7f2f1244b32ed083dbb4cb0c) · [Issue #8](https://github.com/akiyan/MesenCE/issues/8) · [再実行手順](../docs/setup.md)

VDP は 32 bit のフレーム数を持つが、`SmsVdp::GetFrameCount()` が 16 bit で返していたため、本体のフレーム数が 65,536 フレーム（約 18 分）で 0 に戻った（上流から同じ）。
その時点をまたぐ音声の採取は、フレームの不連続として `error` で止まった。32 bit のまま返すようにした。

| 確認 | 結果 |
|---|---|
| `tests/headless_gg_audio.py` | 従来の 2 回の採取が一致し、65,530 フレームから始める採取が 65,536 をまたいで 8 フレーム続けて完了した |
| 本体の試験 6 本（SFC 一括実行、ゲームギア一括実行、名前付きステート、外部制御、PPU、SFC の音声） | 全て通過（ヘッダーの変更のため、全ソースを再ビルドしてから実行） |
| 利用側（kamaitachi-ops） | ゲームギア版の電源投入から 63,800〜66,200 フレームの音を採取できた（修正前は 65,536 で止まった） |
