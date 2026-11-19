# MesenCE akiyan fork の変更情報

直上流は `nesdev-org/MesenCE`。
初回の基準は 2.2.1 の `20ba206cef5ba207c21203176d02cb9f43dda9fb`。
独自コミットのメッセージはこのページの URL とする。 [本体](https://github.com/akiyan/MesenCE/tree/akiyan) · [基準コミット](https://github.com/nesdev-org/MesenCE/commit/20ba206cef5ba207c21203176d02cb9f43dda9fb)

## Linux 向けヘッドレス実行

`make headless` で、本体と同じエミュレーションコアを使う `bin/mesen-headless` をビルドする。
実行時に ROM、Lua スクリプト、新規または空の作業プロファイルを指定する。
SFC は 1P 標準パッド、初期 RAM ゼロ、フレームスキップ無効の設定で起動する。
Lua から入力、メモリ、画面を観測し、`emu.stop(code)` で結果を終了コードに渡す。
プロセスはタイムアウトを終了コード 124 で報告する。 [CLI の仕様](https://github.com/akiyan/MesenCE/blob/akiyan/docs/headless.md)

## 名前付きステート

停止中のセッションで `save 名前` と `load 名前` を使う。
エミュレーターの状態、完了フレーム数、押下中のボタンを 1 ファイルに保存する。
復元前に ROM、パッチ、実行ファイルとコア、設定、状態形式、ファイルのチェックサムを照合する。
`--state-dir` で共有する保存先を指定すると、新しいプロファイルから同じステートを読める。 [仕様](https://github.com/akiyan/MesenCE/blob/akiyan/docs/states.md) · [Issue #1](https://github.com/akiyan/MesenCE/issues/1)

## フレーム単位の外部制御

`--control` で Unix ドメインソケットを開く。
フレーム送りは指定フレーム数、`cancel`、期限切れ、切断で止まり、再接続して観測や続行ができる。
応答には停止理由、完了フレーム、マスタークロックを含む。 [仕様](https://github.com/akiyan/MesenCE/blob/akiyan/docs/control.md) · [Issue #2](https://github.com/akiyan/MesenCE/issues/2)

## PPU のスナップショットと走査線トレース

Lua から CPU・WRAM と画面の状態を取得し、観測時点と描画済みフレームの時刻を照合できる。
フレーム内の PPU レジスタ、DMA、HDMA、割り込みを走査線とクロック付きで記録する。 [仕様](https://github.com/akiyan/MesenCE/blob/akiyan/docs/ppu.md) · [Issue #3](https://github.com/akiyan/MesenCE/issues/3)

## WAV と APU イベント

指定フレーム分のミキサー出力を WAV に記録する。
CPU と SPC700 のポート通信、DSP への書き込み、サンプル位置をエミュレーター内の時刻で比較できる。 [仕様](https://github.com/akiyan/MesenCE/blob/akiyan/docs/audio.md) · [Issue #4](https://github.com/akiyan/MesenCE/issues/4)
