# 導入

Linux で C++17 対応の GCC、make、SDL2 の開発用パッケージを用意する。
試験の実行には Python 3 を使う。

```sh
git clone --branch akiyan https://github.com/akiyan/MesenCE.git mesence
cd mesence
make USE_GCC=true LTO=false -j4 headless
python3 tests/headless_snes.py
```

試験は自作 LoROM を生成し、B ボタンを読むフレーム、WRAM の条件、PNG を確認する。
新しいプロファイルから同じ入力を再実行し、観測結果を比較する。
実行ファイルと作業先は試験の `--binary` と `--work-dir` で指定できる。 [試験コード](https://github.com/akiyan/MesenCE/blob/akiyan/tests/headless_snes.py)

個別の採取では ROM と Lua スクリプトを指定する。
Lua はメモリや映像の採取結果をファイルに書き出せる。

```sh
bin/mesen-headless --home /absolute/path/to/new-profile --timeout 30 +  /absolute/path/to/input.sfc /absolute/path/to/probe.lua
```

終了コード、プロファイル、Lua の使い方は本体の文書を参照する。 [CLI の仕様](https://github.com/akiyan/MesenCE/blob/akiyan/docs/headless.md)
