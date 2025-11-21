import os
import json
import tqdm
import xml.etree.ElementTree as ET

def ends_with_ending_punctuation(s):
    ending_punctuation = ('.', '?', '!')
    return any(s.endswith(char) for char in ending_punctuation)

def concat(title, content):
    if ends_with_ending_punctuation(title.strip()):
        return title.strip() + " " + content.strip()
    else:
        return title.strip() + ". " + content.strip()

def extract_text(element):
    text = (element.text or "").strip()

    for child in element:
        text += (" " if len(text) else "") + extract_text(child)
        if child.tail and len(child.tail.strip()) > 0:
            text += (" " if len(text) else "") + child.tail.strip()
    return text.strip()

def is_subtitle(element):
    if element.tag != 'p':
        return False
    if len(list(element)) != 1:
        return False
    if list(element)[0].tag != 'bold':
        return False
    if list(element)[0].tail and len(list(element)[0].tail.strip()) > 0:
        return False
    return True

def extract(fpath):
    fname = fpath.split("/")[-1].replace(".nxml", "")
    tree = ET.parse(fpath)
    title = tree.getroot().find(".//title").text
    sections = tree.getroot().findall(".//sec")
    saved_text = []
    j = 0
    last_text = None
    for sec in sections:
        sec_title = sec.find('./title').text.strip()
        sub_title = ""
        prefix = " -- ".join([title, sec_title])
        last_text = None
        last_json = None
        last_node = None
        for ch in sec:
            if is_subtitle(ch):
                last_text = None
                last_json = None
                sub_title = extract_text(ch)
                prefix = " -- ".join(prefix.split(" -- ")[:2] + [sub_title])
            elif ch.tag == 'p':
                curr_text = extract_text(ch)
                if len(curr_text) < 200 and last_text is not None and len(last_text + curr_text) < 1000:
                    last_text = " ".join([last_json['content'], curr_text])
                    last_json = {"id": last_json['id'], "title": last_json['title'], "content": last_text}
                    last_json["contents"] = concat(last_json["title"], last_json["content"])
                    saved_text[-1] = json.dumps(last_json)
                else:
                    last_text = curr_text
                    last_json = {"id": '_'.join([fname, str(j)]), "title": prefix, "content": curr_text}
                    last_json["contents"] = concat(last_json["title"], last_json["content"])
                    saved_text.append(json.dumps(last_json))
                    j += 1
            elif ch.tag == 'list':
                list_text = [extract_text(c) for c in ch]
                if last_text is not None and len(" ".join(list_text) + last_text) < 1000:
                    last_text = " ".join([last_json["content"]] + list_text)
                    last_json = {"id": last_json['id'], "title": last_json['title'], "content": last_text}
                    last_json["contents"] = concat(last_json["title"], last_json["content"])
                    saved_text[-1] = json.dumps(last_json)
                elif len(" ".join(list_text)) < 1000:
                    last_text = " ".join(list_text)
                    last_json = {"id": '_'.join([fname, str(j)]), "title": prefix, "content": last_text}
                    last_json["contents"] = concat(last_json["title"], last_json["content"])
                    saved_text.append(json.dumps(last_json))
                    j += 1
                else:
                    last_text = None
                    last_json = None                    
                    for c in list_text:
                        saved_text.append(json.dumps({"id": '_'.join([fname, str(j)]), "title": prefix, "content": c, "contents": concat(prefix, c)}))
                        j += 1
                if last_node is not None and is_subtitle(last_node):
                    sub_title = ""
                    prefix = " -- ".join([title, sec_title])
            last_node = ch
    return saved_text

def process_statpearls_corpus(corpus_dir="/data/multi-agent_snuh/MedRAG/corpus/statpearls", verbose=True):
    """
    Process StatPearls XML files into JSONL format for MedRAG.

    Args:
        corpus_dir: Directory containing the StatPearls corpus
        verbose: Whether to print progress messages

    Returns:
        Number of files processed
    """
    source_dir = os.path.join(corpus_dir, "statpearls_NBK430685")
    chunk_dir = os.path.join(corpus_dir, "chunk")

    if verbose:
        print(f"Processing StatPearls corpus...")
        print(f"Source: {source_dir}")
        print(f"Output: {chunk_dir}")

    fnames = sorted([fname for fname in os.listdir(source_dir) if fname.endswith("nxml")])

    if verbose:
        print(f"Found {len(fnames)} XML files to process")

    if not os.path.exists(chunk_dir):
        os.makedirs(chunk_dir)
        if verbose:
            print(f"Created chunk directory: {chunk_dir}")

    iterator = tqdm.tqdm(fnames) if verbose else fnames
    for fname in iterator:
        fpath = os.path.join(source_dir, fname)
        saved_text = extract(fpath)
        if len(saved_text) > 0:
            output_file = os.path.join(chunk_dir, fname.replace(".nxml", ".jsonl"))
            with open(output_file, 'w') as f:
                f.write('\n'.join(saved_text))

    if verbose:
        print(f"\nProcessing complete! Generated {len(fnames)} JSONL files in {chunk_dir}")

    return len(fnames)


if __name__ == "__main__":
    process_statpearls_corpus()