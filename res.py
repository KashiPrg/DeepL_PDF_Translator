class RegularExpressions:
    # このリストに含まれる正規表現に当てはまる文字列から翻訳を開始する
    start_lines = [r"[0-9]+\s*\.?\s*introduction", r"introduction$"]
    # このリストに含まれる正規表現に当てはまる文字列で翻訳を打ち切る
    end_lines = [r"^references?$"]

    # このリストに含まれる正規表現に当てはまる文字列は無視する
    ignore_lines = [
        r"^\s*ACM Trans",
        r"^\s*[0-9]*:[0-9]*\s*$",   # ページ数
        r"^\s*[0-9]*\s*of\s*[0-9]*\s*$",     # ページ数
        r"^\s*.\s*$",   # なにか一文字しか無い 後でユーザが何文字まで無視するか設定できるようにしたい
        r"^.*(.{1,3}\s+){10,}.*$",  # ぶつ切れの語が極端に多い
        r"Peng Wang, Lingjie Liu, Nenglun Chen, Hung-Kuo Chu, Christian Theobalt, and Wenping Wang$",
        r"^\s*Multimodal Technologies and Interact\s*",
        r"^www.mdpi.com/journal/mti$",
        r"^\s*Li et al\.\s*$",
        r"^\s*Exertion-Aware Path Generation\s*$"
    ]

    # フォーマットの都合上どうしても入ってしまうノイズを置換する
    # これはそのノイズ候補のリスト
    # 一般的な表現の場合は諸刃の剣となるので注意
    # また、リストの最初に近いほど優先して処理される
    replace_source = [
        r"\s*[0-9]+\s*of\s*[0-9]+\s*",   # "1 of 9" などのページカウント
        r"\s*Li et al\.\s*"
    ]
    # ノイズをどのような文字列に置換するか
    replace_target = [
        " ",
        " "
    ]

    # markdown用の置換リスト
    markdown_replace_source = [
        "•"
    ]
    markdown_replace_target = [
        "-"
    ]

    # このリストに含まれる正規表現に当てはまる文字列がある行で改行する
    return_lines = [
        r"(\.|:|;|\([0-9]+\))\s*$",   # 文末(計算式や箇条書きなども含む)
        r"^\s*([0-9]+\s*\.\s*)+.{3,45}\s*$",    # 見出し
        r"^\s*([0-9]+\s*\.\s*)*[0-9]+\s*.{3,45}\s*$",    # 見出し ↑よりも条件が緩いので注意
        r"^([0-9]+\s*\.?)?\s*introduction$",    # 数字がない場合にも対応
        r"^([0-9]+\s*\.?)?\s*related works?$",
        r"^([0-9]+\s*\.?)?\s*overview$",
        r"^([0-9]+\s*\.?)?\s*algorithm$",
        r"^([0-9]+\s*\.?)?\s*experimental results?$",
        r"^([0-9]+\s*\.?)?\s*conclusions?$",
        r"^([0-9]+\s*\.?)?\s*acknowledgements?$",
        r"^([0-9]+\s*\.?)?\s*references?$"
    ]
    # このリストに含まれる正規表現に当てはまる文字列があるとき、
    # 改行対象でも改行しない
    # 主にその略語の後に文が続きそうなものが対象
    # 単なる略語は文末にも存在し得るので対象外
    # 参考：[参考文献リストやデータベースに出てくる略語・用語一覧]
    # (https://www.dl.itc.u-tokyo.ac.jp/gacos/supportbook/16.html)
    return_ignore_lines = [
        r"\s+(e\.g|et al|etc|ex)\.$",
        r"\s+(ff|figs?)\.$",
        r"\s+(i\.e|illus)\.$",
        r"\s+ll\.$",
        r"\s+(Mr|Ms|Mrs)\.$",
        r"\s+(pp|par|pt)\.$",
        r"\s+sec\.$",
        # "["が始まっているが"]"で閉じられていない(参考文献表記の途中など)
        r"\[(?!.*\]).*$"
    ]

    # markdown方式で出力する時、この正規表現に当てはまる行を見出しとして扱う
    header_lines = [
        r"^\s*([0-9]+\s*\.\s*)+.{3,45}\s*$",     # "1.2.3. aaaa" などにヒット
        r"^\s*([0-9]+\s*\.\s*)*[0-9]+\s*.{3,45}\s*$",    # "1.2.3 aaaa" などにヒット
        r"^([0-9]+\s*\.?)?\s*introduction$",    # 数字がない場合にも対応
        r"^([0-9]+\s*\.?)?\s*related works?$",
        r"^([0-9]+\s*\.?)?\s*overview$",
        r"^([0-9]+\s*\.?)?\s*algorithm$",
        r"^([0-9]+\s*\.?)?\s*experimental results?$",
        r"^([0-9]+\s*\.?)?\s*conclusions?$",
        r"^([0-9]+\s*\.?)?\s*acknowledgements?$",
        r"^([0-9]+\s*\.?)?\s*references?$"
    ]
    # 見出しの大きさを決定するためのパターン
    # header_linesの要素と対応する形で記述する
    header_depth_count = [
        r"[0-9]+\s*\.\s*",  # 1.2.3. の"数字."の数が多いほど見出しが小さくなる(#の数が多くなる)
        r"[0-9]+",
        r"^$",
        r"^$",
        r"^$",
        r"^$",
        r"^$",
        r"^$",
        r"^$",
        r"^$"
    ]
    # 見出しの日本語訳の先頭の数字などを消すためのパターン
    header_japanese_remove = [
        r"[0-9]+\s*\.\s*",
        r"\s*([0-9]+\s*\.\s*)*[0-9]+\s*",
        r"[0-9]+\s*\.\s*",
        r"[0-9]+\s*\.\s*",
        r"[0-9]+\s*\.\s*",
        r"[0-9]+\s*\.\s*",
        r"[0-9]+\s*\.\s*",
        r"[0-9]+\s*\.\s*",
        r"[0-9]+\s*\.\s*",
        r"[0-9]+\s*\.\s*"
    ]
    # 見出しの最大の大きさ 1が最大で6が最小
    # header_linesの要素と対応する形で記述する
    header_max_size = [
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2
    ]
