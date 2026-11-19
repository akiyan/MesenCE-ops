# MesenCE-ops

`nesdev-org/MesenCE` を直接フォークした `akiyan/MesenCE` の変更情報、導入手順、検証記録を管理する。
実装と試験、機能や不具合の Issue は本体に置く。 [MesenCE 本体](https://github.com/akiyan/MesenCE/tree/akiyan) · [Issue](https://github.com/akiyan/MesenCE/issues)

既定ブランチの `akiyan` は、固定した上流コミットに独自差分を 1 コミット載せる。
初回は MesenCE 2.2.1 を基準に、Linux 向けのヘッドレス CLI と自作 SFC ROM の試験を加えた。 [変更情報](mesence_akiyan_fork.md) · [上流 2.2.1](https://github.com/nesdev-org/MesenCE/releases/tag/2.2.1)

- [導入と試験](docs/setup.md)
- [上流への追従](docs/upstream-sync.md)
- [初回の検証記録](releases/2026-11-19.md)
- [名前付きステート・外部制御・画面・音声の検証記録](releases/2026-11-19-automation.md)
- [本体の CLI 文書（英語）](https://github.com/akiyan/MesenCE/blob/akiyan/docs/headless.md)

外部ブリッジ方式の実装は上流の `mesen-for-ai` を参照する。 [上流リポジトリ](https://github.com/paulomanrique/mesen-for-ai)

ここに置く文書は MIT ライセンス。本体のライセンスは上流に従う。
公開試験の ROM は試験コードから生成する。 [文書のライセンス](LICENSE) · [本体のライセンス](https://github.com/akiyan/MesenCE/blob/akiyan/LICENSE)
