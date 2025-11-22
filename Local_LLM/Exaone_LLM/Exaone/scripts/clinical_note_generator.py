# -*- coding: utf-8 -*-
"""
Clinical Note Generator - Ollama API 직접 호출 방식
Exaone 3.5 7.8B 모델을 사용하여 다양한 형식의 Clinical Note를 생성합니다.

생성되는 Note 종류:
1. 초진기록 Foundation (한글/영어) - 진단 및 배치 제외
2. 초진기록 정답 (한글/영어) - 진단 및 배치만 포함
3. 전주기 Clinical Note (한글/영어) - 모든 데이터 포함
"""

import os
import sys
import requests
import json
from datetime import datetime

# 모듈 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import LLM_CONFIG
from data_extractor import PatientDataExtractor


class ClinicalNoteGenerator:
    """
    Clinical Note 생성 클래스

    Ollama API를 직접 호출하여 6가지 타입의 Clinical Note를 생성합니다.
    """

    def __init__(self, data_path):
        """
        Clinical Note Generator 초기화

        Args:
            data_path (str): SNUH 데이터 경로
        """
        self.base_url = LLM_CONFIG["base_url"].replace("/v1", "")  # http://localhost:11434
        self.model = LLM_CONFIG["model"]
        self.temperature = LLM_CONFIG["temperature"]
        self.max_tokens = LLM_CONFIG["max_tokens"]

        # 데이터 추출기 초기화
        self.extractor = PatientDataExtractor(data_path=data_path)

        # 양식 파일 로드
        self.templates = self._load_templates()

        print("[OK] Clinical Note Generator 초기화 완료")
        print(f"  - Ollama URL: {self.base_url}")
        print(f"  - Model: {self.model}")

    def _load_templates(self):
        """양식 파일을 로드합니다."""
        template_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        templates = {}
        template_files = {
            "foundation_korean": "초진기록 Clinical Note [Foundation] (한글).txt",
            "foundation_english": "초진기록 Clinical Note [Foundation] (영어).txt",
            "answer_korean": "초진기록 Clinical Note [정답] (한글).txt",
            "answer_english": "초진기록 Clinical Note [정답] (영어).txt",
            "full_cycle_korean": "전주기 Clinical Note [Template] (한글).txt",
            "full_cycle_english": "전주기 Clinical Note [Template] (영어).txt"
        }

        for key, filename in template_files.items():
            filepath = os.path.join(template_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    templates[key] = f.read()
                print(f"[OK] 양식 로드 완료: {filename}")
            except Exception as e:
                print(f"[WARN] 양식 로드 실패: {filename} - {e}")
                templates[key] = ""

        return templates

    def _call_ollama_api(self, prompt, language="korean", timeout=900, max_tokens=None):
        """
        Ollama API를 직접 호출합니다.

        Args:
            prompt (str): LLM에 전달할 프롬프트
            language (str): 'korean' 또는 'english'
            timeout (int): 타임아웃 시간(초)
            max_tokens (int, optional): 최대 생성 토큰 수 (None이면 기본값 사용)

        Returns:
            str: 생성된 텍스트
        """
        url = f"{self.base_url}/api/generate"

        # max_tokens가 지정되지 않으면 기본값 사용
        if max_tokens is None:
            max_tokens = self.max_tokens

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": max_tokens
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=timeout)
            response.raise_for_status()

            result = response.json()
            return result.get("response", "")

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Ollama API 호출 실패: {e}")
            return f"Error: {str(e)}"

    def _format_patient_data(self, patient_data):
        """환자 데이터를 프롬프트용 텍스트로 포맷팅합니다 (초진 기록용)."""
        text = f"""환자 ID: {patient_data['patient_id']}

=== 기본 정보 ===
- 나이: {patient_data['기본정보']['나이']}세
- 성별: {patient_data['기본정보']['성별']}
- 내원 시각: {patient_data['기본정보']['내원시각']}
- 내원 방법: {patient_data['기본정보']['내원방법']}
- ESI 레벨: {patient_data['기본정보']['ESI']}
- 퇴실 정보: {patient_data['기본정보']['퇴실정보']}

=== 활력징후 ===
{self._format_list(patient_data['활력징후'])}

=== 진단명 ===
{self._format_list(patient_data['진단명'])}

=== 투여 약물 ===
{self._format_list(patient_data['약품'])}

=== 진료기록 ===
{self._format_list(patient_data['진료기록'])}

=== 진단검사 ===
{self._format_list(patient_data['진단검사'])}

=== 영상검사 ===
{self._format_list(patient_data['영상검사'])}

=== 기능검사 ===
{self._format_list(patient_data['기능검사'])}

=== 초기간호기록 ===
{self._format_list(patient_data['초기간호기록'])}"""

        return text

    def _format_full_cycle_data(self, patient_data):
        """전주기 Clinical Note용 전체 데이터를 프롬프트용 텍스트로 포맷팅합니다 (13개 파일 전체)."""
        text = f"""환자 ID: {patient_data['patient_id']}

=== 기본 정보 ===
- 나이: {patient_data['기본정보']['나이']}세
- 성별: {patient_data['기본정보']['성별']}
- 내원 시각: {patient_data['기본정보']['내원시각']}
- 내원 방법: {patient_data['기본정보']['내원방법']}
- ESI 레벨: {patient_data['기본정보']['ESI']}
- 퇴실 정보: {patient_data['기본정보']['퇴실정보']}

=== 활력징후 ===
{self._format_list(patient_data['활력징후'])}

=== 진단명 ===
{self._format_list(patient_data['진단명'])}

=== 투여 약물 ===
{self._format_list(patient_data['약품'])}

=== 진료기록 ===
{self._format_list(patient_data['진료기록'])}

=== 진단검사 ===
{self._format_list(patient_data['진단검사'])}

=== 영상검사 ===
{self._format_list(patient_data['영상검사'])}

=== 기능검사 ===
{self._format_list(patient_data['기능검사'])}

=== 초기간호기록 ===
{self._format_list(patient_data['초기간호기록'])}

=== 수혈/CP ===
{self._format_list(patient_data.get('수혈_CP', '정보 없음'))}

=== 타과의뢰 ===
{self._format_list(patient_data.get('타과의뢰', '정보 없음'))}

=== 퇴실간호기록 ===
{self._format_list(patient_data.get('퇴실간호기록', '정보 없음'))}

=== 간호일지 ===
{self._format_list(patient_data.get('간호일지', '정보 없음'))}"""

        return text

    def _format_list(self, data):
        """리스트나 문자열 데이터를 포맷팅"""
        if isinstance(data, list):
            if not data:
                return "정보 없음"
            return "\n".join([f"  - {item}" for item in data])
        return str(data)

    def generate_foundation_note(self, patient_data, language="korean"):
        """
        초진기록 Foundation Note 생성 (진단 및 배치 제외)

        Args:
            patient_data (dict): 환자 데이터
            language (str): 'korean' 또는 'english'

        Returns:
            str: 생성된 Clinical Note
        """
        template_key = f"foundation_{language}"
        template = self.templates.get(template_key, "")

        data_text = self._format_patient_data(patient_data)

        if language == "korean":
            prompt = f"""당신은 응급실 의료 기록 전문가입니다.
다음 환자 데이터를 바탕으로 초진기록 Clinical Note [Foundation] 형식으로 작성해주세요.

아래 양식 예시를 참고하여 동일한 구조로 작성하되, 주어진 환자 데이터에 맞게 내용을 채워주세요.

=== 양식 예시 ===
{template}

=== 환자 데이터 ===
{data_text}

위 환자 데이터를 바탕으로 초진기록 Clinical Note [Foundation]을 작성해주세요.
[최종 진단(Diagnosis)]과 [배치(Disposition)] 섹션은 제외하고 작성합니다.

**절대 금지**: 문서 마지막에 "이 기록은...", "본 노트는...", "이 Clinical Note는..." 등 어떠한 추가 설명, 요약, 코멘트도 붙이지 마세요."""
        else:
            prompt = f"""You are an emergency department medical record specialist.
Please write an Initial Record Clinical Note [Foundation] based on the following patient data.

**IMPORTANT: Write the entire note in ENGLISH only.**

Refer to the template example below and write in the same structure, but fill in the content according to the given patient data.

=== Template Example ===
{template}

=== Patient Data ===
{data_text}

Please write the Initial Record Clinical Note [Foundation] based on the above patient data.
Exclude the [Diagnosis] and [Disposition] sections.

**STRICTLY FORBIDDEN**: Do NOT add any explanations, summaries, or comments at the end like "This note...", "This Clinical Note...", etc."""

        print(f"\n{'='*60}")
        print(f"초진기록 Foundation 생성 중 ({language.upper()})...")
        print(f"{'='*60}")

        result = self._call_ollama_api(prompt, language)
        print(f"[OK] 초진기록 Foundation 생성 완료 ({language.upper()})")

        return result

    def generate_answer_note(self, patient_data, language="korean"):
        """
        초진기록 정답 Note 생성 (진단 및 배치만 포함)

        Args:
            patient_data (dict): 환자 데이터
            language (str): 'korean' 또는 'english'

        Returns:
            str: 생성된 Clinical Note
        """
        template_key = f"answer_{language}"
        template = self.templates.get(template_key, "")

        data_text = self._format_patient_data(patient_data)

        if language == "korean":
            prompt = f"""당신은 응급실 의료 기록 전문가입니다.
다음 환자 데이터를 바탕으로 초진기록 Clinical Note [정답] 형식으로 작성해주세요.

아래 양식 예시를 참고하여 동일한 구조로 작성하되, 주어진 환자 데이터에 맞게 내용을 채워주세요.

=== 양식 예시 ===
{template}

=== 환자 데이터 ===
{data_text}

위 환자 데이터를 바탕으로 초진기록 Clinical Note [정답]을 작성해주세요.
[최종 진단(Diagnosis)]과 [배치(Disposition)] 섹션만 포함합니다.

**절대 금지**: 문서 마지막에 어떠한 추가 설명, 요약, 코멘트도 붙이지 마세요."""
        else:
            prompt = f"""You are an emergency department medical record specialist.
Please write an Initial Record Clinical Note [Answer] based on the following patient data.

**IMPORTANT: Write the entire note in ENGLISH only.**

Refer to the template example below and write in the same structure, but fill in the content according to the given patient data.

=== Template Example ===
{template}

=== Patient Data ===
{data_text}

Please write the Initial Record Clinical Note [Answer] based on the above patient data.
Include only the [Diagnosis] and [Disposition] sections.

**STRICTLY FORBIDDEN**: Do NOT add any explanations, summaries, or comments at the end."""

        print(f"\n{'='*60}")
        print(f"초진기록 정답 생성 중 ({language.upper()})...")
        print(f"{'='*60}")

        result = self._call_ollama_api(prompt, language)
        print(f"[OK] 초진기록 정답 생성 완료 ({language.upper()})")

        return result

    def generate_full_cycle_note(self, patient_data, language="korean"):
        """
        전주기 Clinical Note 생성 (모든 데이터 포함 - 13개 파일 전체)

        Args:
            patient_data (dict): 환자 데이터 (전주기용 추가 데이터 포함)
            language (str): 'korean' 또는 'english'

        Returns:
            str: 생성된 Clinical Note
        """
        # 전주기용 전체 데이터 포맷팅 사용
        data_text = self._format_full_cycle_data(patient_data)

        if language == "korean":
            prompt = f"""당신은 응급실 의료 기록 전문가입니다.
다음 환자 데이터를 바탕으로 전주기 Clinical Note를 작성해주세요.

전주기 Clinical Note는 환자의 응급실 내원부터 퇴실까지의 전체 과정을 상세하게 기록하는 문서입니다.
제공된 모든 환자 데이터(13개 파일)를 포함하여 다음 구조로 작성해주세요:

[전주기 Clinical Note]

[기본 정보(Basic Information)]
- 환자 ID, 나이, 성별, 내원 시각, 내원 방법, ESI 레벨

[임상 증상(Clinical Presentation)]
- 주 증상, 내원 사유
- 활력징후 (모든 측정값)
- ESI 레벨

[신체 진찰(Physical Examination)]
- 전반적 상태, 신경학적 검사, 근골격계, 흉부, 복부 등

[관련 의학적 병력(Related Medical History)]
- 과거 진단명 (모든 진단)
- 현재 복용 약물
- 알레르기 정보

[초기 검사 결과(Initial Lab Results)]
- 진단검사 (모든 검사 결과)
- 영상검사
- 기능검사

[응급실 경과(ED Course)]
- 투여된 약물 및 처치 (모든 항목)
- 수혈/CP (해당시)
- 경과 관찰

[간호 기록(Nursing Records)]
- 초기간호기록
- 간호일지 (모든 기록)
- 퇴실간호기록

[타과의뢰(Consultation)]
- 의뢰 내용 및 결과 (해당시)

[최종 진단(Diagnosis)]
- 주 진단명
- 부 진단명

[배치(Disposition)]
- 퇴실 정보 및 사유

=== 환자 데이터 (13개 파일 전체) ===
{data_text}

위 환자 데이터의 모든 정보를 빠짐없이 포함하여 전주기 Clinical Note를 작성해주세요.

**절대 금지**: 문서 마지막에 "이 기록은...", "본 노트는...", "이 Clinical Note는...", "본 전주기 Clinical Note는..." 등 어떠한 추가 설명, 요약, 코멘트도 붙이지 마세요. [배치(Disposition)] 섹션으로 끝내세요."""
        else:
            prompt = f"""You are an emergency department medical record specialist.
Please write a Full Cycle Clinical Note based on the following patient data.

**IMPORTANT: Write the entire note in ENGLISH only.**

A Full Cycle Clinical Note records the entire process from the patient's arrival to discharge from the emergency department in detail.
Please write using the following structure, including all provided patient data (13 files):

[Full Cycle Clinical Note]

[Basic Information]
- Patient ID, Age, Gender, Arrival Time, Arrival Method, ESI Level

[Clinical Presentation]
- Chief Complaint, Reason for Visit
- Vital Signs (all measurements)
- ESI Level

[Physical Examination]
- General Status, Neurological Exam, Musculoskeletal, Chest, Abdomen, etc.

[Related Medical History]
- Past Medical Diagnoses (all diagnoses)
- Current Medications
- Allergy Information

[Initial Lab Results]
- Diagnostic Tests (all test results)
- Imaging Studies
- Functional Tests

[ED Course]
- Medications and Treatments Administered (all items)
- Transfusion/CP (if applicable)
- Clinical Progress

[Nursing Records]
- Initial Nursing Records
- Nursing Notes (all records)
- Discharge Nursing Records

[Consultation]
- Consultation content and results (if applicable)

[Diagnosis]
- Primary Diagnosis
- Secondary Diagnoses

[Disposition]
- Discharge Information and Rationale

=== Patient Data (All 13 Files) ===
{data_text}

Please write a Full Cycle Clinical Note including all information from the above patient data without omission.

**STRICTLY FORBIDDEN**: Do NOT add any explanations, summaries, or comments at the end like "This note...", "This Clinical Note...", "This Full Cycle Clinical Note comprehensively...", etc. End with the [Disposition] section only."""

        print(f"\n{'='*60}")
        print(f"전주기 Clinical Note 생성 중 ({language.upper()})...")
        print(f"  [참고] 긴 프롬프트로 인해 시간이 걸릴 수 있습니다 (최대 10분)")
        print(f"{'='*60}")

        # 전주기 노트는 더 긴 타임아웃(600초)과 더 많은 토큰(4000) 사용
        result = self._call_ollama_api(prompt, language, timeout=600, max_tokens=4000)
        print(f"[OK] 전주기 Clinical Note 생성 완료 ({language.upper()})")

        return result

    def save_notes(self, patient_id, notes):
        """
        생성된 6개의 Note를 환자별 폴더에 저장합니다.

        Args:
            patient_id: 환자 ID
            notes (dict): 6개의 생성된 Note
                - foundation_korean
                - foundation_english
                - answer_korean
                - answer_english
                - full_cycle_korean
                - full_cycle_english
        """
        # 환자별 폴더 생성
        output_base = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data",
            "output_notes"
        )
        patient_folder = os.path.join(output_base, str(patient_id))
        os.makedirs(patient_folder, exist_ok=True)

        # 파일명 매핑
        file_mapping = {
            "foundation_korean": f"초진기록_Foundation_한글_{patient_id}.txt",
            "foundation_english": f"초진기록_Foundation_영어_{patient_id}.txt",
            "answer_korean": f"초진기록_정답_한글_{patient_id}.txt",
            "answer_english": f"초진기록_정답_영어_{patient_id}.txt",
            "full_cycle_korean": f"전주기_Clinical_Note_한글_{patient_id}.txt",
            "full_cycle_english": f"전주기_Clinical_Note_영어_{patient_id}.txt"
        }

        saved_files = []
        for note_type, filename in file_mapping.items():
            if note_type in notes:
                filepath = os.path.join(patient_folder, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(notes[note_type])
                saved_files.append(filename)
                print(f"  [SAVED] {filename}")

        print(f"\n[OK] 환자 {patient_id}: {len(saved_files)}개 파일 저장 완료")
        print(f"  저장 위치: {patient_folder}")

        return patient_folder

    def process_patient(self, patient_id):
        """
        한 명의 환자에 대해 6개의 Note를 생성하고 저장합니다.

        Args:
            patient_id: 환자 ID

        Returns:
            str: 저장된 폴더 경로
        """
        print(f"\n{'='*70}")
        print(f"환자 {patient_id} 처리 시작")
        print(f"{'='*70}")

        # 초진기록용 환자 데이터 포맷팅
        patient_data = self.extractor.format_for_clinical_note(patient_id)

        # 6개 Note 생성
        notes = {}

        # 1-2. 초진기록 Foundation (한글/영어)
        notes['foundation_korean'] = self.generate_foundation_note(patient_data, language="korean")
        notes['foundation_english'] = self.generate_foundation_note(patient_data, language="english")

        # 3-4. 초진기록 정답 (한글/영어)
        notes['answer_korean'] = self.generate_answer_note(patient_data, language="korean")
        notes['answer_english'] = self.generate_answer_note(patient_data, language="english")

        # 전주기용 추가 데이터 로드
        print("\n[INFO] 전주기용 추가 데이터 로딩 중...")
        self.extractor.extract_full_cycle_data([patient_id])

        # 전주기용 전체 데이터 포맷팅
        full_cycle_data = self.extractor.format_for_full_cycle_note(patient_id)

        # 5-6. 전주기 Clinical Note (한글/영어) - 13개 파일 전체 데이터 사용
        notes['full_cycle_korean'] = self.generate_full_cycle_note(full_cycle_data, language="korean")
        notes['full_cycle_english'] = self.generate_full_cycle_note(full_cycle_data, language="english")

        # 파일 저장
        folder_path = self.save_notes(patient_id, notes)

        print(f"\n{'='*70}")
        print(f"[완료] 환자 {patient_id} 처리 완료!")
        print(f"{'='*70}")

        return folder_path

    def process_all_patients(self, test_mode=True):
        """
        모든 환자 또는 테스트 환자 1명을 처리합니다.

        Args:
            test_mode (bool): True면 1명만, False면 전체 환자
        """
        print("\n" + "="*70)
        print("Clinical Note Generator - 환자 데이터 처리 시작")
        print("="*70)

        # 환자 데이터 로드
        limit = 1 if test_mode else None
        all_patient_data = self.extractor.extract_all(limit=limit)
        patient_ids = list(all_patient_data.keys())

        if test_mode:
            print(f"\n[테스트 모드] {len(patient_ids)}명의 환자만 처리합니다.")
        else:
            print(f"\n[전체 모드] {len(patient_ids)}명의 환자를 처리합니다.")

        # 각 환자 처리
        for patient_id in patient_ids:
            try:
                self.process_patient(patient_id)
            except Exception as e:
                print(f"\n[ERROR] 환자 {patient_id} 처리 중 오류 발생: {e}")
                import traceback
                traceback.print_exc()

        print("\n" + "="*70)
        print(f"[완료] 총 {len(patient_ids)}명의 환자 처리 완료!")
        print("="*70)


def main():
    """메인 실행 함수"""
    print("\n" + "="*70)
    print("Clinical Note Generator - Exaone 3.5 7.8B")
    print("Ollama API 직접 호출 방식")
    print("="*70)

    # 데이터 경로 설정
    data_path = r"C:\Users\jojk6\SNUH_EME\Multi_Agent_EME\Local_LLM\Exaone_LLM\data\SNUH_Data"

    # Generator 초기화
    try:
        generator = ClinicalNoteGenerator(data_path=data_path)
    except Exception as e:
        print(f"\n[ERROR] Generator 초기화 실패: {e}")
        print("\nOllama가 실행 중인지 확인하세요:")
        print("  1. 명령 프롬프트에서 'ollama serve' 실행")
        print("  2. 또는 'ollama run exaone3.5:7.8b' 실행")
        sys.exit(1)

    # 전체 환자 처리 (GPU 환경용)
    generator.process_all_patients(test_mode=False)


if __name__ == "__main__":
    main()
