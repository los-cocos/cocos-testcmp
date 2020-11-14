"""
Sintax
  python %s subcommand

Subcommands:
  --help: shows this text and exit
  --list-symbols: outputs symbols in template_cmp_report.htm to symbols.txt
  --rename-symbols: renames symbols in file template_cmp_report.htm as
      specified in file renaming_symbols.txt; outputs to file
      template_cmp_report_symbols_renamed.htm
  --proofread: renders template to file cmp_report_proofread.htm by replacing
      @symbol -> SYMBOL

When used as a module, you probably want to use funcs
  render_template_to_file(in_, out, symbols)
  render_delta(snp_by_scripts, reldir_snp_ref, reldir_snp_other)
"""
import os
import re
import sys

listing_known_symbols = """
cmp.cached
cmp.ordinal
cmp.v_other.asked_cocos
cmp.v_other.asked_py
cmp.v_other.asked_pyglet
cmp.v_other.cached
cmp.v_other.pytest_link
cmp.v_other.pytest_summary
cmp.v_other.report_link
cmp.v_other.resolved_cocos
cmp.v_other.resolved_py
cmp.v_other.resolved_pyglet
cmp.v_other.stats_blacks
cmp.v_other.stats_failures
cmp.v_other.stats_no_testinfo
cmp.v_other.stats_repeteables
cmp.v_other.stats_total_tests
cmp.v_ref.asked_cocos
cmp.v_ref.asked_py
cmp.v_ref.asked_pyglet
cmp.v_ref.cached
cmp.v_ref.pytest_link
cmp.v_ref.pytest_summary
cmp.v_ref.report_link
cmp.v_ref.resolved_cocos
cmp.v_ref.resolved_py
cmp.v_ref.resolved_pyglet
cmp.v_ref.stats_blacks
cmp.v_ref.stats_failures
cmp.v_ref.stats_no_testinfo
cmp.v_ref.stats_repeteables
cmp.v_ref.stats_total_tests
section_cmp_snp_diff"""

known_symbols = listing_known_symbols.strip().split("\n")

def get_template_symbols(text):
    amp_symbols = re.findall(r'@[\w\.-]+', text)
    symbols = [s[1:] for s in amp_symbols]
    return sorted(symbols)


def dump_template_symbols(fname):
    with open(fname, "r", encoding="utf-8") as f:
        text = f.read()
    symbols = get_template_symbols(text)
    symbols_listing = "\n".join(symbols)
    as_bytes = symbols_listing.encode("utf-8")
    i = fname.rfind(".")
    outname = fname[: i + 1] + "symbols.txt"
    with open(outname, "wb") as f:
        f.write(as_bytes)

def list_symbols():
    fname = "template_cmp_report.htm"
    dump_template_symbols(fname)

###

# re.finditer(pattern, string, flags=0)
# Return an iterator yielding MatchObject instances over all
 # non-overlapping matches for the RE pattern in string.
 # The string is scanned left-to-right, and matches are returned in the
  # order found. Empty matches are included in the result.

def render_template(text, symbols):
    parts = []
    index_after_last_match = 0
    for match in re.finditer(r'@[\w\.-]+', text):
        startindex, endindex = match.span()
        # handle chars before match
        parts.append(text[index_after_last_match: startindex])
        index_after_last_match = endindex
        # handle matched symbol
        symbol = text[startindex + 1 : endindex]
        symbol_value = symbols[symbol]
        parts.append(symbol_value)
    # handle chars after last match
    parts.append(text[index_after_last_match:])
    text_out = "".join(parts)
    return text_out

    as_bytes = text_out.encode("utf8")

def render_template_to_file(in_, out, symbols):
    with open(in_, "r", encoding="utf-8") as f:
        text = f.read()
    text_out = render_template(text, symbols)
    as_bytes = text_out.encode("utf-8")
    with open(out, "wb") as f:
        f.write(as_bytes)

def dump_cmp_proofread():
    syms = { s: s.upper() for s in known_symbols}
    in_ = "template_cmp_report.htm"
    out = "cmp_report_proofread.htm"
    render_template_to_file(in_, out, syms)

def parses_symbols_renaming(text, separator):
    """ parses rename spec

    blank lines or lines starting with '#' are ignored
    one rename per line
    each line must be
    <old>[<separtator><new>]
    separator can be multicharacter, like "->"
    separator can be " " if symbols don't have embeded spaces
    """
    all_lines = text.split("\n")
    old_to_new = {}
    for line in all_lines:
        s = line.strip()
        if len(s)==0 or s.startswith("#"):
            continue
        parts = s.split(separator)
        if len(parts)==1:
            parts.append(parts[0])
        parts = [s.strip() for s in parts]
        old_to_new[parts[0]] = parts[1]
    return old_to_new

def rename_symbols():
    fname = "renaming_symbols.txt"
    with open(fname, "r", encoding="utf-8") as f:
        rename_listing = f.read()
    old_to_new = parses_symbols_renaming(rename_listing, "->")
    print(old_to_new)
    amp_symbols = {k: "@" + v for k, v in old_to_new.items()}
    in_ = "template_cmp_report.htm"
    out = "template_cmp_report_symbols_renamed.htm"
    render_template_to_file(in_, out, amp_symbols)

### section snapshots delta
def render_delta(snp_by_scripts, reldir_snp_ref, reldir_snp_other):
    "scripts_with_non_matching_snapshots"
    n = len(snp_by_scripts)
    parts = ["<p>num tests with at least one different snapshot: %d</p>" % n]
    if n:
        parts.append("<h2>Details differences</h2>")
        m = '<table><tr><td><img src="%s"></td><td><img src="%s"></td></tr></table>'
        for name in snp_by_scripts:
            parts.append("<h3>Script: %s</h3>" % name)
            print("in render delta - script: ", name)
            print("differents:", snp_by_scripts[name])
            for snp_name, delta_1, delta_2 in snp_by_scripts[name]:
                parts.append("<p>pic: %s</p>" % snp_name)
                link1 = reldir_snp_ref + "/" + snp_name
                link2 = reldir_snp_other + "/" + snp_name
                parts.append(m % (link1, link2))
                if delta_1 is None:
                    parts.append("Different size or image mode, no diff.")
                else:
                    parts.append(m % (delta_1, delta_2))                    
    text = "\n".join(parts)
    return text

def usage():
    script_name = os.path.basename(sys.argv[0])
    print(__doc__ % script_name)

def unknown_subcmd():
    print("Unknown subcommand.")
    usage()
    sys.exit(1)

subcmd = {
    "--list-symbols": list_symbols,
    "--rename-symbols": rename_symbols,
    "--proofread": dump_cmp_proofread,
    "--help": usage,
    "-h": usage,
    "unknown_subcmd": unknown_subcmd,
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        selector = "--help"
    else:
        selector = sys.argv[1]
        if selector not in subcmd:
            selector = "unknown_subcmd"
    subcmd[selector]()
