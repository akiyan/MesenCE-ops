# 導入

Linux で C++17 対応の GCC、make、SDL2 の開発用パッケージを用意する。
試験の実行には Python 3 を使う。

```sh
git clone --branch akiyan https://github.com/akiyan/MesenCE.git mesence
cd mesence
make USE_GCC=true LTO=false -j4 headless
python3 tests/headless_snes.py
python3 tests/headless_gg.py
python3 tests/headless_states.py
python3 tests/headless_control.py
python3 tests/headless_ppu.py
python3 tests/headless_audio.py
python3 tests/headless_gg_audio.py
python3 tests/headless_video.py
```

各試験は自作 LoROM（`headless_gg.py` はゲームギアの ROM）を生成する。
名前付きステートの復元と入力リプレイ、実行の中断・続行、画面と走査線の観測、音声と APU イベント、ゲームギアの音声と PSG の書き込み、画素のバイト列を個別に確認する。
実行ファイルと作業先は試験の `--binary` と `--work-dir` で指定できる。 [試験コード](https://github.com/akiyan/MesenCE/blob/akiyan/tests/headless_snes.py)

個別の採取では ROM と Lua スクリプトを指定する。
Lua はメモリや映像の採取結果をファイルに書き出せる。

```sh
bin/mesen-headless --home /absolute/path/to/new-profile --timeout 30 +  /absolute/path/to/input.sfc /absolute/path/to/probe.lua
```

終了コード、プロファイル、Lua の使い方は本体の文書を参照する。 [CLI の仕様](https://github.com/akiyan/MesenCE/blob/akiyan/docs/headless.md)

## 常駐セッション

`--control` を指定すると ROM を開き、外部クライアントから最初の実行要求を待つ。
別のプロファイルでも名前付きステートを使う場合は `--state-dir` で共通のディレクトリを指定する。

```sh
bin/mesen-headless --home /absolute/path/to/new-profile \
  --state-dir /absolute/path/to/states --control /absolute/path/to/control.sock input.sfc
```

コマンドと応答の形式は本体の文書を参照する。 [外部制御](https://github.com/akiyan/MesenCE/blob/akiyan/docs/control.md) · [名前付きステート](https://github.com/akiyan/MesenCE/blob/akiyan/docs/states.md)
