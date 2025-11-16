# -*- coding: utf-8 -*-
"""
Admin Agent - Clinical Note 생성 에이전트
AutoGen Framework를 사용하여 환자 데이터를 Clinical Note로 변환합니다.
"""

import os
import sys
from autogen import AssistantAgent
import json
from datetime import datetime

# 모듈 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import get_api_key, LLM_CONFIG
from data_extractor import PatientDataExtractor


class AdminAgent:
    """
    Admin Agent 클래스

    환자 데이터를 입력받아 AutoGen을 통해 Clinical Note를 생성합니다.
    한글과 영어 버전을 각각 생성합니다.
    """

    def __init__(self):
        """
        Admin Agent 초기화
        - OpenAI API key 로딩
        - AutoGen AssistantAgent 설정
        """
        # API key 로딩
        self.api_key = get_api_key()

        # LLM 설정
        self.llm_config = {
            "model": LLM_CONFIG["model"],
            "api_key": self.api_key,
            "temperature": LLM_CONFIG["temperature"],
            "max_tokens": LLM_CONFIG["max_tokens"]
        }

        # AutoGen AssistantAgent 생성 (한글용)
        self.korean_agent = AssistantAgent(
            name="Korean_Clinical_Note_Writer",
            system_message="""당신은 응급실 의료 기록 전문가입니다.
환자 데이터를 받아 한국 응급실 진료 기록(Primary Consultation) 형식으로 작성합니다.

다음 형식을 반드시 따라주세요:

[기본 정보(Basic Information)]
- 나이, 성별, 내원 시각, 내원 방법 등을 자연스러운 문장으로 작성

[임상 증상(Clinical Presentation)]
- 주 증상과 내원 사유를 상세히 기술
- 활력징후 포함
- ESI 레벨 명시

[신체 진찰(Physical Examination)]
- 초기 간호 기록을 바탕으로 신체 검진 소견 작성

[관련 의학적 병력(Related Medical History)]
- 과거 진단명 및 병력
- 현재 복용 중인 약물
- 알레르기 정보

[초기 검사 결과(Initial Lab Results)]
- 진단검사, 영상검사, 기능검사 결과 요약

[응급실 경과(ED Course)]
- 투여된 약물 및 처치 내용

[최종 진단(Diagnosis)]
- 주 진단명 및 부 진단명

[배치(Disposition)]
- 퇴실 정보 및 사유

환자 데이터를 받으면 위 형식으로 자연스럽고 전문적인 한글 Clinical Note를 작성해주세요.""",
            llm_config=self.llm_config
        )

        # AutoGen AssistantAgent 생성 (영어용)
        self.english_agent = AssistantAgent(
            name="English_Clinical_Note_Writer",
            system_message="""You are an emergency department medical record specialist.
Convert patient data into a Primary Consultation format used in emergency departments.

Follow this structure:

[Basic Information]
- Age, gender, arrival time, arrival method in natural sentences

[Clinical Presentation]
- Chief complaint and reason for visit
- Vital signs
- ESI level

[Physical Examination]
- Physical exam findings based on initial nursing records

[Related Medical History]
- Past medical history and diagnoses
- Current medications
- Allergies

[Initial Lab Results]
- Summary of diagnostic tests, imaging, and functional tests

[ED Course]
- Medications and treatments administered

[Diagnosis]
- Primary and secondary diagnoses

[Disposition]
- Discharge information and rationale

When you receive patient data, write a natural and professional Clinical Note in English following the above format.""",
            llm_config=self.llm_config
        )

        print("[OK] Admin Agent 초기화 완료")
        print(f"  - Model: {LLM_CONFIG['model']}")
        print(f"  - Temperature: {LLM_CONFIG['temperature']}")

    def create_prompt_from_data(self, patient_data):
        """
        환자 데이터를 LLM 프롬프트로 변환합니다.

        Args:
            patient_data (dict): 포맷팅된 환자 데이터

        Returns:
            str: LLM에 전달할 프롬프트
        """
        prompt = f"""다음은 환자의 응급실 데이터입니다. 이 데이터를 바탕으로 Primary Consultation 형식의 Clinical Note를 작성해주세요.

환자 ID: {patient_data['patient_id']}

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

위 데이터를 종합하여 자연스러운 Clinical Note를 작성해주세요."""

        return prompt

    def _format_list(self, data):
        """리스트나 문자열 데이터를 포맷팅"""
        if isinstance(data, list):
            if not data:
                return "정보 없음"
            return "\n".join([f"  - {item}" for item in data])
        return str(data)

    def generate_clinical_note(self, patient_data, language="korean"):
        """
        Clinical Note를 생성합니다.

        Args:
            patient_data (dict): 포맷팅된 환자 데이터
            language (str): 'korean' 또는 'english'

        Returns:
            str: 생성된 Clinical Note
        """
        # 프롬프트 생성
        prompt = self.create_prompt_from_data(patient_data)

        # 언어에 따라 적절한 에이전트 선택
        agent = self.korean_agent if language == "korean" else self.english_agent

        print(f"\n{'='*60}")
        print(f"Clinical Note 생성 중 ({language.upper()})...")
        print(f"{'='*60}")

        # AutoGen을 통해 Clinical Note 생성
        try:
            # generate_reply 메서드 사용
            response = agent.generate_reply(
                messages=[{"role": "user", "content": prompt}]
            )

            clinical_note = response if isinstance(response, str) else str(response)

            print(f"[OK] Clinical Note 생성 완료 ({language.upper()})")
            return clinical_note

        except Exception as e:
            print(f"[FAIL] Clinical Note 생성 실패: {str(e)}")
            return f"Error: {str(e)}"

    def save_clinical_note(self, clinical_note, patient_id, language="korean"):
        """
        생성된 Clinical Note를 파일로 저장합니다.

        Args:
            clinical_note (str): 생성된 Clinical Note
            patient_id: 환자 ID
            language (str): 'korean' 또는 'english'
        """
        # 출력 폴더 생성
        output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data",
            "output_notes"
        )
        os.makedirs(output_dir, exist_ok=True)

        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{patient_id}_{language}_{timestamp}.txt"
        filepath = os.path.join(output_dir, filename)

        # 파일 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(clinical_note)

        print(f"[OK] Clinical Note 저장 완료: {filename}")
        return filepath


def main():
    """
    메인 실행 함수
    """
    print("\n" + "="*60)
    print("Admin Agent - Clinical Note 생성 시스템")
    print("="*60 + "\n")

    # 1. 환자 데이터 추출
    print("1단계: 환자 데이터 추출")
    print("-" * 60)
    extractor = PatientDataExtractor(data_path="../../Data")
    all_patient_data = extractor.extract_all()

    # 2. Admin Agent 초기화
    print("\n2단계: Admin Agent 초기화")
    print("-" * 60)
    admin_agent = AdminAgent()

    # 3. 각 환자에 대해 Clinical Note 생성
    print("\n3단계: Clinical Note 생성")
    print("-" * 60)

    for patient_id in all_patient_data.keys():
        print(f"\n환자 ID: {patient_id}")
        print("=" * 60)

        # 환자 데이터 포맷팅
        formatted_data = extractor.format_for_clinical_note(patient_id)

        # 한글 Clinical Note 생성
        korean_note = admin_agent.generate_clinical_note(formatted_data, language="korean")
        korean_path = admin_agent.save_clinical_note(korean_note, patient_id, language="korean")

        # 영어 Clinical Note 생성
        english_note = admin_agent.generate_clinical_note(formatted_data, language="english")
        english_path = admin_agent.save_clinical_note(english_note, patient_id, language="english")

        print(f"\n환자 {patient_id} Clinical Note 생성 완료!")
        print(f"  - 한글: {os.path.basename(korean_path)}")
        print(f"  - 영어: {os.path.basename(english_path)}")

    print("\n" + "="*60)
    print("[OK] 모든 Clinical Note 생성 완료!")
    print("="*60)


if __name__ == "__main__":
    main()
