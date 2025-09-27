def compare_texts(original_text, modified_text):
    """원본/변경 텍스트를 단어 단위로 비교하여 차이 목록을 생성."""
    original_words = original_text.split()
    modified_words = modified_text.split()
    
    changes = []
    
    for i, word in enumerate(modified_words):
        if i >= len(original_words) or word != original_words[i]:
            changes.append({
                'word': word,
                'action': 'added' if i >= len(original_words) else 'modified',
                'original': original_words[i] if i < len(original_words) else None
            })
    
    for i in range(len(original_words)):
        if i >= len(modified_words) or original_words[i] != modified_words[i]:
            changes.append({
                'word': original_words[i],
                'action': 'removed',
                'modified': modified_words[i] if i < len(modified_words) else None
            })
    
    return changes

def get_changed_words(original_text, modified_text):
    """추가/수정/삭제된 단어들의 유니크 리스트 반환."""
    changes = compare_texts(original_text, modified_text)
    seen = set()
    result = []
    for ch in changes:
        w = ch.get('word')
        if w and w not in seen:
            seen.add(w)
            result.append(w)
    return result

def generate_word_list(changes):
    """변경 내역(changes)에서 단어/작업(action)만 추출한 요약 리스트 생성."""
    word_list = []
    for change in changes:
        word_info = {
            'word': change['word'],
            'action': change['action']
        }
        word_list.append(word_info)
    return word_list

def get_word_meaning(word):
    """단어 의미 조회 (플레이스홀더)."""
    return "{} 의 의미 (플레이스홀더)".format(word)

def get_example_sentence(word):
    """예문 조회 (플레이스홀더)."""
    return "{} 사용 예문 (플레이스홀더)".format(word)