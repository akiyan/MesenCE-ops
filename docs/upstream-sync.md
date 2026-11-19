# 上流への追従

`master` は直上流の追従用ブランチ。
`akiyan` の親は検証に使う上流リビジョンとし、独自変更を 1 コミットにまとめる。 [直上流](https://github.com/nesdev-org/MesenCE) · [変更情報](../mesence_akiyan_fork.md)

1. 本体の未コミット変更を確認し、`origin` と `upstream` を fetch する。
2. 公開中の `origin/akiyan` の SHA を控え、タグで保持する。
3. 上流を更新するときは新しい基準から独自コミットを cherry-pick する。機能の追加は同じコミットに amend する。
4. 本体の試験を実行し、新しい基準との差分が 1 コミットであることを確認する。
5. 変更情報と検証記録を更新し、本体は手順 2 のリモート SHA を指定した `--force-with-lease` で更新する。
6. 利用側の固定リビジョンを更新する。 [試験手順](setup.md)
