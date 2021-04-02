import re
import wx

from deeplmanager import DeepLManager
from pathlib import Path
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError
from res import RegularExpressions
from settings import Settings


def PDFTranslate(filename):
    textlines = PDFTextExtract(filename)

    setting_ignore_start_condition = not Settings.RegularExpressions.StartLines.enabled_overall
    setting_ignore_end_condition = not Settings.RegularExpressions.EndLines.enabled_overall

    if textlines is None:
        # ファイルがそもそもPDFではなかったとき
        wx.MessageBox(filename + "はPDF形式ではありません。", "notPDF")
        return False
    elif len(textlines) == 0:
        # PDFではあったがテキストが抽出できなかったとき、
        # 開始条件に引っかからなかったか、終了条件に引っかかりまくったかの可能性を考慮して、
        # それらを無視するか聞き、どちらか片方でも無視するならもう一度抽出を行う
        while True:
            ignore_start_condition = False
            ignore_end_condition = False
            # もともとは無視しない設定だったなら、開始条件の無視を問う
            if not setting_ignore_start_condition:
                message_ignore_start_condition = wx.MessageBox(
                    filename + "からテキストが抽出されませんでした。\n翻訳開始条件を無視して翻訳を行いますか？",
                    caption="テキストの抽出に失敗",
                    style=wx.YES | wx.NO)
                if message_ignore_start_condition == wx.YES:
                    ignore_start_condition = True

            # もともとは無視しない設定だったなら、終了条件の無視を問う
            if not setting_ignore_end_condition:
                message_ignore_end_condition = wx.MessageBox(
                    "翻訳終了条件" + ("も" if ignore_start_condition else "を") + "無視しますか？",
                    caption="テキストの抽出に失敗",
                    style=wx.YES | wx.NO)
                if message_ignore_end_condition == wx.YES:
                    ignore_end_condition = True

            if ignore_start_condition or ignore_end_condition:
                # どちらか片方でも無視するように変更するならもう一度抽出を行う
                textlines = PDFTextExtract(filename, ignore_start_condition, ignore_end_condition)
            else:
                # そうでない(元の設定でどちらも無視するようになっていたり、
                # 無視するように設定し直さない)なら失敗と見なす
                wx.MessageBox(filename + "からテキストが抽出されませんでした。", caption="テキストの抽出に失敗")
                return False

            # 何かが抽出できたならループを抜け出して続行する
            # 再び何も抽出できなかったら(抽出条件を変えるかもしれないので)もう一度繰り返す
            if len(textlines) != 0:
                break

    # 抽出したテキストを翻訳単位ごとにまとめる
    tl_units = OrganizeTranslationUnits(filename, textlines)

    # 翻訳の実行と翻訳結果の書き込み
    TranslateAndWrite(filename, tl_units)

    return True


def PDFTextExtract(filename, force_ignore_start_condition=False, force_ignore_end_condition=False):
    """
    渡されたPDFファイルからテキストを抽出し、各種条件によって加工を施して返す
    outputから始まる各種引数をTrueにすることで、各種条件にヒットする行をtxtファイルとして出力する

    Args:
        filename (string): 抽出対象のPDFファイル名
        force_ignore_start_condition (bool, optional): 翻訳開始条件の無視を強制する
        force_ignore_end_condition (bool, optional): 翻訳終了条件の無視を強制する

    Returns:
        list of string: ファイルがPDFでない場合はNone
        翻訳開始条件に該当しないなどでテキストを抽出できなかった場合は空リスト
        それ以外の場合は抽出・加工したテキスト
    """
    # 出力をMarkdown式にするか
    output_type_markdown = Settings.output_type_markdown
    # 翻訳開始/終了条件を無いものとして扱うか
    setting_ignore_start_condition = not Settings.RegularExpressions.StartLines.enabled_overall
    setting_ignore_end_condition = not Settings.RegularExpressions.EndLines.enabled_overall
    # 各種条件に該当する行をtxtファイルとして出力するか
    output_start_lines = Settings.RegularExpressions.StartLines.output_hit_lines
    output_end_lines = Settings.RegularExpressions.EndLines.output_hit_lines
    output_ignore_lines = Settings.RegularExpressions.IgnoreLines.output_hit_lines
    output_replace_source_lines = Settings.RegularExpressions.ReplaceParts.Standard.output_hit_lines
    output_markdown_replace_source_lines = Settings.RegularExpressions.ReplaceParts.Markdown.output_hit_lines
    output_header_lines = Settings.RegularExpressions.HeaderLines.output_hit_lines

    # PDFからテキストを抽出
    textlines = []
    try:
        textlines = extract_text(filename).splitlines()
    except PDFSyntaxError:
        # ドロップされたファイルがPDFでない場合はNone
        return None

    # 抽出したテキストから空行を除く
    temp = list(filter(lambda s: s != "", textlines))

    # 出力用のディレクトリを作成
    Path("output").mkdir(exist_ok=True)

    # 条件に該当する行を出力するためのファイル群
    file_path = str(Path("output/" + Path(filename).stem))
    f_start = None
    f_end = None
    f_ignore = None
    f_replace = None
    f_markdown_replace = None
    f_header = None
    if output_start_lines:
        f_start = open(file_path + "_Start.txt", mode="w", encoding="utf-8")
    if output_end_lines:
        f_end = open(file_path + "_End.txt", mode="w", encoding="utf-8")
    if output_ignore_lines:
        f_ignore = open(file_path + "_Ignore.txt", mode="w", encoding="utf-8")
    # これ以降のファイルで、正規表現に引っかかっているのに記載されていない行がある場合は、
    # 無視条件に引っかかって削除されている可能性がある
    if output_replace_source_lines:
        f_replace = open(file_path + "_Replace.txt", mode="w", encoding="utf-8")
    # これ以降のファイルで、正規表現に引っかかっているのに記載されていない行がある場合は、
    # 置換条件に引っかかって置換されている可能性がある
    if output_markdown_replace_source_lines:
        f_markdown_replace = open(file_path + "_MarkdownReplace.txt", mode="w", encoding="utf-8")
    # これ以降のファイルで、正規表現に引っかかっているのに記載されていない行がある場合は、
    # Markdown出力時の置換条件に引っかかって置換されている可能性がある
    if output_header_lines:
        f_header = open(file_path + "_Header.txt", mode="w", encoding="utf-8")

    # 除くべき行を除く
    textlines = []
    lines_extracting = False    # テキストを抽出中か
    skipLine = False            # その行を飛ばすか
    # 開始条件を無視する場合
    if setting_ignore_start_condition or force_ignore_start_condition:
        lines_extracting = True
    for t in temp:
        # 翻訳を開始する合図となる文字列を探す
        for sl in RegularExpressions.start_lines:
            if re.search(sl, t, flags=re.IGNORECASE):
                if output_start_lines:
                    f_start.write(sl + ", " + t + "\n")
                if not (setting_ignore_start_condition or force_ignore_start_condition):
                    lines_extracting = True
                break
        # 翻訳を打ち切る合図となる文字列を探す
        for el in RegularExpressions.end_lines:
            if re.search(el, t, flags=re.IGNORECASE):
                if output_end_lines:
                    f_end.write(el + ", " + t + "\n")
                if not (setting_ignore_end_condition or force_ignore_end_condition):
                    lines_extracting = False
                break
        # 翻訳をしないことになったなら、その文字列は飛ばす
        if not lines_extracting:
            continue

        # 翻訳を開始しても、無視する文字列なら飛ばす
        for il in RegularExpressions.ignore_lines:
            if re.search(il, t, flags=re.IGNORECASE):
                skipLine = True
                if output_ignore_lines:
                    f_ignore.write(il + ", " + t + "\n")
                break
        if skipLine:
            skipLine = False
            continue

        # 置換すべき文字列があったなら置換する
        for ri in range(len(RegularExpressions.replace_source)):
            if output_replace_source_lines and re.search(RegularExpressions.replace_source[ri], t):
                f_replace.write(RegularExpressions.replace_source[ri] + ", " + t + "\n")
            t = re.sub(
                RegularExpressions.replace_source[ri],
                RegularExpressions.replace_target[ri],
                t
            )
        for mri in range(len(RegularExpressions.markdown_replace_source)):
            if output_markdown_replace_source_lines and re.search(RegularExpressions.markdown_replace_source[mri], t):
                f_markdown_replace.write(RegularExpressions.markdown_replace_source[mri] + ", " + t + "\n")
            if output_type_markdown:
                t = re.sub(
                    RegularExpressions.markdown_replace_source[mri],
                    RegularExpressions.markdown_replace_target[mri],
                    t
                )

        if output_header_lines:
            # 見出し条件に引っかかる場合は出力
            for hl in RegularExpressions.header_lines:
                if re.search(hl, t, flags=re.IGNORECASE):
                    f_header.write(hl + ", " + t + "\n")
                    break

        textlines.append(t)

    # ファイルクローズ
    if output_start_lines:
        f_start.close()
    if output_end_lines:
        f_end.close()
    if output_ignore_lines:
        f_ignore.close()
    if output_replace_source_lines:
        f_replace.close()
    if output_markdown_replace_source_lines:
        f_markdown_replace.close()
    if output_header_lines:
        f_header.close()

    # 抽出・加工したテキストを返す
    return textlines


def OrganizeTranslationUnits(filename, textlines, tl_unit_max_len=4800):
    """
    PDFから抽出・加工したテキストから翻訳単位(DeepLで一回に翻訳する段落の集まり)を構成し、そのリストを返す

    Args:
        textlines (list of string): PDFから抽出・加工したテキストのリスト
        tl_unit_max_len (int, optional): 翻訳単位の最大の長さ(無料版DeepLの制限が5000字まで)

    Returns:
        2D-list of string: 翻訳単位のリスト
    """
    output_chart_start_lines = Settings.RegularExpressions.ChartStartLines.output_hit_lines
    output_return_lines = Settings.RegularExpressions.ReturnLines.Possibility.output_hit_lines
    output_return_ignore_lines = Settings.RegularExpressions.ReturnLines.Ignore.output_hit_lines
    # 出力用のディレクトリを作成
    Path("output").mkdir(exist_ok=True)
    # 条件に該当する行を出力するためのファイル群
    file_path = str(Path("output/" + Path(filename).stem))
    f_chart = None
    f_return = None
    f_return_ignore = None
    if output_chart_start_lines:
        f_chart = open(file_path + "_Chart.txt", mode="w", encoding="utf-8")
    if output_return_lines:
        f_return = open(file_path + "_Return.txt", mode="w", encoding="utf-8")
    if output_return_ignore_lines:
        f_return_ignore = open(file_path + "_ReturnIgnore.txt", mode="w", encoding="utf-8")

    tl_units = []   # 翻訳単位(4800字以内でまとめられた段落群)のリスト
    too_long_flags = []     # それぞれの翻訳単位が4800字を超えているか否かのリスト
    paragraphs = []     # 段落ごとに分けて格納
    parslen = 0         # paragraphsの総文字数
    par_buffer = ""     # 今扱っている段落の文字列
    chart_buffer = ""   # 図表の説明の文字列
    chartParagraph = False     # 図表の説明の段落を扱っているフラグ
    tooLongParagraph = False    # 長過ぎる段落を扱っているフラグ
    for i in range(len(textlines)):
        # 図表の説明は本文を寸断している事が多いため、
        # 図表を示す文字列が文頭に現れた場合は別口で処理する
        # 例：Fig. 1. | Figure2: | Table 3. など
        if re.search(r"^(Fig\.|Figure|Table)\s*\d+(\.|:)", textlines[i], flags=re.IGNORECASE):
            # ヒット時の保存処理を入れる
            chartParagraph = True

        # 待ち時間を短くするために、DeepLの制限ギリギリまで文字数を詰める
        # 現在扱っている文字列までの長さを算出
        currentLen = parslen + len(textlines[i])
        if chartParagraph:
            currentLen += len(chart_buffer)
        else:
            currentLen += len(par_buffer)

        if not tooLongParagraph and currentLen > tl_unit_max_len:
            # 1翻訳単位の制限文字数(既定値4800)を超えそうになったら、それまでの段落を翻訳にかける
            if parslen > 0:
                tl_units.append(paragraphs)
                too_long_flags.append(False)

                parslen = 0
                paragraphs = []
            # 1段落で5000文字を超えるなら、手動での翻訳をお願いする
            else:
                tooLongParagraph = True

        # 文末っぽい表現がされていたり、
        # その他return_linesに含まれる正規表現に当てはまればそこを文末と見なす
        return_flag = False
        for rl in RegularExpressions.return_lines:
            if re.search(rl, textlines[i], flags=re.IGNORECASE):
                if output_return_lines:
                    f_return.write(rl + ", " + textlines[i] + "\n")
                return_flag = True
                break

        # ただし、よくある略語だったりする場合は文末とは見なさない
        if return_flag:
            for ril in RegularExpressions.return_ignore_lines:
                if re.search(ril, textlines[i]):
                    if output_return_ignore_lines:
                        f_return_ignore.write(ril + ", " + textlines[i] + "\n")
                    return_flag = False
                    break

        end_of_file = i == len(textlines) - 1   # ファイルの終端フラグ
        # 文末かファイル終端の場合
        if return_flag or end_of_file:
            # 今までのバッファと今扱っている行をひとまとめにする
            temp = ""
            if chartParagraph:
                temp = chart_buffer + textlines[i]
                chart_buffer = ""
            else:
                temp = par_buffer + textlines[i]
                par_buffer = ""
            # 5000字を超える一段落は、自動での翻訳を行わない
            # ファイルの終端でもそれは変わらない
            if tooLongParagraph:
                tl_units.append([temp])
                too_long_flags.append(True)
            else:
                # 長すぎない場合は翻訳待ちの段落として追加
                parslen += len(temp)
                paragraphs.append(temp)
                # ファイルの終端の場合は最後に翻訳と書き込みを行う
                if end_of_file:
                    tl_units.append(paragraphs)
                    too_long_flags.append(False)
            chartParagraph = False
        else:
            # 文末でない場合は末尾に適切な処理を施す
            temp = ""
            if textlines[i][-1] == "-":
                # 文末がハイフンなら除く
                temp = textlines[i][:-1]
            else:
                # そうでないならスペース追加
                temp = textlines[i] + " "
            # バッファに追加
            if chartParagraph:
                chart_buffer += temp
            else:
                par_buffer += temp

    # ファイルクローズ
    if output_chart_start_lines:
        f_chart.close()
    if output_return_lines:
        f_return.close()
    if output_return_ignore_lines:
        f_return_ignore.close()

    return tl_units


def TranslateAndWrite(filename, tl_units):
    # 翻訳先の言語
    lang = Settings.target_language_for_translate
    # 翻訳文を一文ごとに改行するか
    add_target_return = Settings.add_target_return
    # 出力をMarkdown式にするか
    output_type_markdown = Settings.output_type_markdown
    # 原文を出力するか
    output_source = Settings.output_source
    # Markdown形式において、原文をコメントとして出力するか
    source_as_comment = Settings.source_as_comment

    # 出力用のディレクトリを作成
    Path("output").mkdir(exist_ok=True)
    # 出力用ファイルのパス
    outputFilePath = Path("output/" + Path(filename).stem + ".txt")

    with open(outputFilePath, mode="w", encoding="utf-8") as f:
        for paragraphs in tl_units:
            translated = DeepLManager.translate("\n".join(paragraphs), lang).splitlines()

            tl_processed = []
            for tl in translated:
                if add_target_return:
                    # 翻訳文を一文ごとに改行する
                    if output_type_markdown:
                        # Markdown方式の改行
                        tl = re.sub(r"(。|．)", "。  \n", tl)
                    else:
                        # 通常の改行
                        tl = re.sub(r"(。|．)", "。\n", tl)
                else:
                    # 改行しない
                    tl = re.sub(r"．", "。", tl)    # 句点を統一
                tl_processed.append(tl)

            for i in range(len(paragraphs)):
                # Markdown方式で出力する場合は見出しに#を加える
                header_line_hit = False
                if output_type_markdown:
                    for j in range(len(RegularExpressions.header_lines)):
                        if re.search(RegularExpressions.header_lines[j], paragraphs[i], flags=re.IGNORECASE):
                            header_line_hit = True
                            # 見出しの深さを算出 & #を出力
                            depth = max(1, len(re.findall(
                                RegularExpressions.header_depth_count[j],
                                paragraphs[i])))
                            f.write("#" * min(RegularExpressions.header_max_size[j] + depth - 1, 6) + " ")

                            # 原文の出力を行う場合
                            if output_source:
                                # 原文の見出しとその直下に見出しの日本語訳を出力
                                f.write(paragraphs[i] + "\n")
                                # 日本語の見出し部分の先頭(1.2.など)を削除
                                tl_processed[i] = re.sub(
                                    RegularExpressions.header_target_remove[j],
                                    "", tl_processed[i])

                            f.write(tl_processed[i] + ("\n" if tl_processed[i][-1] == "\n" else "\n\n"))
                            break
                    if not header_line_hit:
                        if output_source and source_as_comment:
                            # Markdown式の出力かつ原文の出力が有効で、
                            # 見出しでない場合はコメントとして加工する
                            paragraphs[i] = "%%" + paragraphs[i] + "%%"
                if not header_line_hit:
                    # 見出しでない場合の出力
                    if output_source:
                        f.write(paragraphs[i] + "\n\n")
                    f.write(tl_processed[i] + ("\n" if tl_processed[i][-1] == "\n" else "\n\n"))

    DeepLManager.MinimizeWindow()
