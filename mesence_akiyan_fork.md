# MesenCE akiyan fork の変更情報

直上流は `nesdev-org/MesenCE`。
初回の基準は 2.2.1 の `20ba206cef5ba207c21203176d02cb9f43dda9fb`。
独自コミットのメッセージはこのページの URL とする。 [本体](https://github.com/akiyan/MesenCE/tree/akiyan) · [基準コミット](https://github.com/nesdev-org/MesenCE/commit/20ba206cef5ba207c21203176d02cb9f43dda9fb)

## AI エージェント向け操作の比較

公式本家はフォーク元の 2.2.1 が基準です。比較対象はスーパーファミコン（SFC）とゲームギア（GG）です。右の4列は `akiyan` 版の操作経路で、単体 CLI は `mesen-headless` の Lua バッチ実行を指します。 [本家の TestRunner](https://github.com/nesdev-org/MesenCE/blob/20ba206cef5ba207c21203176d02cb9f43dda9fb/UI/Utilities/TestRunner.cs) · [本家の Lua API](https://github.com/nesdev-org/MesenCE/blob/20ba206cef5ba207c21203176d02cb9f43dda9fb/Core/Debugger/LuaApi.cpp)

**✗ 非対応　△ GUI で可　◯ 自動操作可**

機種の指定がないセルは両機種に共通です。`◯ SFC` と `△ SFC` は SFC のみ対応します。

### 公式本家で GUI 操作が必要、または非対応だった操作

| 操作 | 公式本家 | GDB | Unix 制御ソケット | MCP | 単体 CLI |
|---|:---:|:---:|:---:|:---:|:---:|
| フレーム 0 で外部コマンド待ち | ✗ | ✗ | ◯ SFC | ✗ | ✗ |
| 切断時のフレーム停止・再接続 | ✗ | ✗ | ◯ SFC | ✗ | ✗ |
| 空の実行プロファイル指定・初期状態固定 | ✗ | ✗ | ◯ SFC | ✗ | ◯ |
| 名前付きステート（フレーム数・押下込み） | ✗ | ✗ | ◯ SFC | ✗ | ✗ |
| CPU・PPU・WRAM・完成 PNG の時刻付き取得 | ✗ | ✗ | ✗ | ✗ | ◯ SFC |
| ラスタートレース（PPU・DMA・HDMA・割り込み） | △ SFC | ✗ | ✗ | ✗ | ◯ SFC |
| 短区間 WAV 採取 | △ | ✗ | ✗ | ✗ | ◯ |
| WAV と音源イベント（SFC の SPC/DSP、GG の PSG）の同期採取 | ✗ | ✗ | ✗ | ✗ | ◯ |
| 長さを先に決めない全編の録音（WAV のみ） | ✗ | ✗ | ✗ | ✗ | ◯ |
| 全フレームの画素のバイト列での取得（エンコーダーへ直接） | ✗ | ✗ | ✗ | ✗ | ◯ |
| I/O ポートの読み書き監視（GG の PSG など） | ✗ | ✗ | ✗ | ✗ | ◯ GG |

### 公式本家で自動操作でき、操作経路が増えたもの

**←** 本家から引き継いだ経路　**◯** フォークで増えた経路。`Lua ←` は、新設の単体 CLI で本家の Lua API を使うことを示します。

| 操作 | 公式本家 | GDB | Unix 制御ソケット | MCP | 単体 CLI |
|---|:---:|:---:|:---:|:---:|:---:|
| ヘッドレス Lua 起動・終了コード | ◯ `--testRunner` | ✗ | ✗ | ✗ | **◯**（Lua ←） |
| 実時間タイムアウト | ◯ `--testRunner` | ✗ | **◯** SFC | ✗ | **◯** |
| 一時停止・N フレーム送り | ◯ Lua | ✗ | **◯** SFC | ✗ | **◯**（Lua ←） |
| 命令・走査線ステップ | ◯ Lua | ✗ | ✗ | ✗ | **◯**（Lua ←） |
| 条件停止・メモリアクセス監視 | ◯ Lua | ✗ | ✗ | ✗ | **◯**（Lua ←） |
| フレーム・マスタークロック取得 | ◯ Lua | ✗ | **◯** SFC | ✗ | **◯**（Lua ←） |
| RAM 読取 | ◯ Lua | ✗ | **◯** SFC | ✗ | **◯**（Lua ←） |
| CPU 状態取得・メモリ書込 | ◯ Lua | ✗ | ✗ | ✗ | **◯**（Lua ←） |
| パッド操作・フレーム指定の入力列 | ◯ Lua | ✗ | **◯** SFC | ✗ | **◯**（Lua ←） |
| PNG・画素取得 | ◯ Lua | ✗ | ✗ | ✗ | **◯**（Lua ←） |
| ステート保存・復元 | ◯ Lua | ✗ | **◯** SFC | ✗ | **◯**（Lua ←） |

Unix 制御ソケットの `--control` は SFC 専用です。単体 CLI は `.gg` も扱い、ゲームギアの PNG は 160×144 で前フレームとの合成なしです。ゲームギアの Start 入力は Lua の `pause` を使います。 [CLI 仕様](https://github.com/akiyan/MesenCE/blob/akiyan/docs/headless.md) · [ソケット仕様](https://github.com/akiyan/MesenCE/blob/akiyan/docs/control.md)

## Linux 向けヘッドレス実行

`make headless` で、本体と同じエミュレーションコアを使う `bin/mesen-headless` をビルドする。
実行時に ROM、Lua スクリプト、新規または空の作業プロファイルを指定する。
SFC は 1P 標準パッド、初期 RAM ゼロ、フレームスキップ無効の設定で起動する。
Lua から入力、メモリ、画面を観測し、`emu.stop(code)` で結果を終了コードに渡す。
プロセスはタイムアウトを終了コード 124 で報告する。
フレームの待ちを入れず、ホストの速さで動かす（ROM の読み込みで最高速のフラグが消えるため、速度の設定を 0 にする）。 [Issue #6](https://github.com/akiyan/MesenCE/issues/6) [CLI の仕様](https://github.com/akiyan/MesenCE/blob/akiyan/docs/headless.md)

## マスターシステム・ゲームギアの一括実行

ROM と Lua スクリプトによる一括実行で、マスターシステムとゲームギアの ROM も扱う。拡張子 `.gg` でゲームギアになる。
1P に標準パッドを設定し、RAM を 0 で初期化する。画面は各機種の表示範囲（ゲームギアは 160×144）で取得し、ゲームギアの前フレームとの合成はしない。
RAM の初期状態を固定したときは VDP を走査線 0 から始め、同じ入力の実行が同じフレームで進むようにする（上流は電源投入ごとに 0〜200 の乱数）。
常駐の外部制御（`--control`）は SFC のみ。 [仕様](https://github.com/akiyan/MesenCE/blob/akiyan/docs/headless.md) · [Issue #5](https://github.com/akiyan/MesenCE/issues/5)

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

## WAV と音源イベント

指定フレーム分のミキサー出力を WAV に記録する。
SFC は CPU と SPC700 のポート通信、DSP への書き込み、マスターシステムとゲームギアは PSG とステレオの書き込みを、サンプル位置とともにエミュレーター内の時刻で比較できる。
ヘッドレス実行では PSG の各チャンネルを GUI の既定と同じ音量にする（コアの既定は無音）。 [仕様](https://github.com/akiyan/MesenCE/blob/akiyan/docs/audio.md) · [Issue #4](https://github.com/akiyan/MesenCE/issues/4) · [Issue #7](https://github.com/akiyan/MesenCE/issues/7)

## 全編の高速な録画

`emu.getScreenBytes()` は、`emu.getScreenBuffer()` と同じ画素をバイト列（`bgr0`）と幅・高さで返す。画素ごとの表も PNG も作らないため、全フレームを名前付きパイプからエンコーダーへ渡しても、実行の速さがほとんど落ちない。
`emu.startAudioCapture` のイベントのパスに `nil` を渡すと WAV だけを記録する。`emu.stopAudioCapture()` は次のフレームの終わりで採取を完了するので、長さを先に決めなくてよい。採取の上限は 1,080,000 フレーム（5 時間）。 [仕様](https://github.com/akiyan/MesenCE/blob/akiyan/docs/audio.md) · [使い方](https://github.com/akiyan/MesenCE/blob/akiyan/docs/AGENT_GUIDE.md) · [Issue #9](https://github.com/akiyan/MesenCE/issues/9)

## 負荷に左右されないスクリーンショット

`emu.takeScreenshot()` は、映像のデコーダーに渡した最後のフレームの変換が終わるのを待ってから PNG を作る。
デコーダーは別のスレッドで動き、`endFrame` では今終わったフレームがまだ渡っていないため、PNG は 1 つ前のフレームになる。
上流は変換の終わりを待たないので、ホストの負荷が高いと 2 つ前のフレームを返すことがあった。
変換が済んでいれば待たない。今終わったフレームの画素は `emu.getScreenBytes()` で取る。 [仕様](https://github.com/akiyan/MesenCE/blob/akiyan/docs/AGENT_GUIDE.md) · [Issue #10](https://github.com/akiyan/MesenCE/issues/10)

## I/O ポートの監視

Lua のメモリコールバックで `emu.memType.smsPort` を指定すると、マスターシステムとゲームギアの I/O ポートの読み書きで呼ばれる。
上流ではポートに絶対アドレスがないため、このメモリ種別のコールバックが一度も呼ばれなかった。 [仕様](https://github.com/akiyan/MesenCE/blob/akiyan/docs/headless.md) · [Issue #7](https://github.com/akiyan/MesenCE/issues/7)
