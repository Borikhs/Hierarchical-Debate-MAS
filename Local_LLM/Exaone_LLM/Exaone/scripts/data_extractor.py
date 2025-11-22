# -*- coding: utf-8 -*-
"""
환자 데이터 추출 모듈
SNUH 응급실 데이터(13개 파일)에서 처음 2명의 환자 데이터를 추출합니다.
초진 기록 관점에서 필요한 정보만 선택적으로 추출합니다.
"""

import pandas as pd
import os
import sys

# config 모듈 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import INITIAL_CONSULTATION_FILES, EXCLUDED_FILES, FULL_CYCLE_ADDITIONAL_FILES


class PatientDataExtractor:
    """
    환자 데이터 추출 클래스

    초진 기록 작성을 위해 필요한 데이터를 9개 파일에서 추출합니다.
    """

    def __init__(self, data_path="../Data"):
        """
        Args:
            data_path (str): 데이터 파일들이 있는 폴더 경로
        """
        self.data_path = data_path
        self.patient_data = {}

    def load_basic_info(self, limit=None):
        """
        기본정보 파일을 로딩하고 환자 ID를 추출합니다.

        Args:
            limit (int, optional): 읽을 환자 수 제한. None이면 전체 환자

        Returns:
            list: 환자 ID 리스트
        """
        file_path = os.path.join(self.data_path, INITIAL_CONSULTATION_FILES["1_기본정보"])
        df = pd.read_excel(file_path)

        # 환자 데이터 (제한이 있으면 적용)
        if limit is not None:
            patients_df = df.head(limit)
        else:
            patients_df = df

        # 환자 ID 추출 (첫 번째 컬럼)
        patient_ids = patients_df.iloc[:, 0].tolist()

        # 기본정보 저장
        for idx, patient_id in enumerate(patient_ids):
            self.patient_data[patient_id] = {
                "기본정보": patients_df.iloc[idx].to_dict()
            }

        print(f"[OK] 기본정보 로딩 완료: {len(patient_ids)}명의 환자")
        return patient_ids

    def extract_patient_data(self, patient_ids):
        """
        주어진 환자 ID에 대해 모든 관련 데이터를 추출합니다.

        Args:
            patient_ids (list): 추출할 환자 ID 리스트
        """
        for file_key, file_name in INITIAL_CONSULTATION_FILES.items():
            if file_key == "1_기본정보":
                continue  # 이미 로딩됨

            file_path = os.path.join(self.data_path, file_name)

            try:
                df = pd.read_excel(file_path)

                # 각 환자에 대해 데이터 필터링
                for patient_id in patient_ids:
                    # 첫 번째 컬럼이 환자 ID라고 가정
                    patient_records = df[df.iloc[:, 0] == patient_id]

                    if not patient_records.empty:
                        self.patient_data[patient_id][file_key] = patient_records.to_dict('records')
                    else:
                        self.patient_data[patient_id][file_key] = []

                print(f"[OK] {file_key} 로딩 완료")

            except Exception as e:
                print(f"[FAIL] {file_key} 로딩 실패: {str(e)}")
                for patient_id in patient_ids:
                    self.patient_data[patient_id][file_key] = []

    def extract_all(self, limit=None):
        """
        모든 데이터 추출을 수행하는 메인 함수

        Args:
            limit (int, optional): 읽을 환자 수 제한. None이면 전체 환자

        Returns:
            dict: 환자 ID를 키로 하는 전체 데이터 딕셔너리
        """
        print("=" * 60)
        print("SNUH 응급실 환자 데이터 추출 시작")
        print("=" * 60)
        print(f"\n[데이터 경로] {self.data_path}")
        print(f"[사용할 파일] {len(INITIAL_CONSULTATION_FILES)}개")
        print(f"[제외된 파일] {len(EXCLUDED_FILES)}개")
        if limit:
            print(f"[환자 수 제한] {limit}명\n")
        else:
            print(f"[환자 수 제한] 없음 (전체 환자)\n")

        # 제외된 파일 이유 출력
        print("제외된 파일 및 이유:")
        for file_name, reason in EXCLUDED_FILES.items():
            print(f"  - {file_name}: {reason}")
        print()

        # 1. 기본정보에서 환자 ID 추출
        patient_ids = self.load_basic_info(limit=limit)

        # 2. 나머지 파일에서 해당 환자들의 데이터 추출
        self.extract_patient_data(patient_ids)

        print("\n" + "=" * 60)
        print(f"[OK] 데이터 추출 완료: {len(patient_ids)}명의 환자")
        print("=" * 60)

        return self.patient_data

    def format_for_clinical_note(self, patient_id):
        """
        추출된 데이터를 Clinical Note 생성에 적합한 형식으로 변환합니다.

        Args:
            patient_id: 환자 ID

        Returns:
            dict: 정리된 환자 정보
        """
        if patient_id not in self.patient_data:
            raise ValueError(f"환자 ID {patient_id}의 데이터가 없습니다.")

        patient = self.patient_data[patient_id]
        basic_info = patient.get("기본정보", {})

        # 기본정보 추출
        formatted_data = {
            "patient_id": patient_id,
            "기본정보": {
                "나이": self._calculate_age(basic_info),
                "성별": self._get_gender(basic_info),
                "내원시각": self._get_arrival_time(basic_info),
                "내원방법": self._get_arrival_method(basic_info),
                "ESI": self._get_esi(basic_info),
                "퇴실정보": self._get_disposition(basic_info)
            },
            "활력징후": self._format_vital_signs(patient.get("13_활력징후", [])),
            "진단명": self._format_diagnosis(patient.get("2_진단명", [])),
            "약품": self._format_medications(patient.get("4_약품", [])),
            "진료기록": self._format_medical_records(patient.get("5_진료기록", [])),
            "진단검사": self._format_lab_tests(patient.get("7_진단검사", [])),
            "영상검사": self._format_imaging(patient.get("8_영상검사", [])),
            "기능검사": self._format_functional_tests(patient.get("9_기능검사", [])),
            "초기간호기록": self._format_initial_nursing(patient.get("10_초기간호기록", []))
        }

        return formatted_data

    def _calculate_age(self, basic_info):
        """생년월일에서 나이 계산"""
        if not basic_info or len(basic_info) < 4:
            return "정보없음"

        try:
            birth_date = str(list(basic_info.values())[3])
            birth_year = int(birth_date[:4])
            age = 2018 - birth_year
            return age
        except:
            return "정보없음"

    def _get_gender(self, basic_info):
        """성별 추출"""
        if not basic_info or len(basic_info) < 3:
            return "정보없음"
        return list(basic_info.values())[2] if len(basic_info) > 2 else "정보없음"

    def _get_arrival_time(self, basic_info):
        """내원 시각 추출"""
        if not basic_info or len(basic_info) < 9:
            return "정보없음"

        try:
            arrival_dt = str(list(basic_info.values())[8])
            if ' ' in arrival_dt:
                return arrival_dt.split()[1][:5]
            return arrival_dt
        except:
            return "정보없음"

    def _get_arrival_method(self, basic_info):
        """내원 방법 추출"""
        if not basic_info or len(basic_info) < 8:
            return "정보없음"
        return str(list(basic_info.values())[7])

    def _get_esi(self, basic_info):
        """ESI 레벨 추출"""
        if not basic_info or len(basic_info) < 5:
            return "정보없음"
        return str(list(basic_info.values())[4])

    def _get_disposition(self, basic_info):
        """퇴실 정보 추출"""
        if not basic_info or len(basic_info) < 11:
            return "정보없음"
        return str(list(basic_info.values())[10])

    def _format_vital_signs(self, vital_records):
        """활력징후 포맷팅"""
        if not vital_records:
            return "활력징후 데이터 없음"

        vital_list = []
        for record in vital_records[:3]:  # 처음 3개만
            vital_str = ", ".join([f"{k}: {v}" for k, v in record.items() if pd.notna(v)])
            vital_list.append(vital_str)

        return vital_list if vital_list else "활력징후 데이터 없음"

    def _format_diagnosis(self, diagnosis_records):
        """진단명 포맷팅"""
        if not diagnosis_records:
            return []

        diagnoses = []
        for record in diagnosis_records[:5]:  # 최대 5개
            diag_str = " - ".join([str(v) for v in record.values() if pd.notna(v) and v != ''])
            if diag_str:
                diagnoses.append(diag_str)

        return diagnoses

    def _format_medications(self, med_records):
        """약품 포맷팅"""
        if not med_records:
            return []

        medications = []
        for record in med_records[:10]:  # 최대 10개
            med_str = " / ".join([str(v) for v in list(record.values())[1:5] if pd.notna(v) and str(v).strip()])
            if med_str:
                medications.append(med_str)

        return medications

    def _format_medical_records(self, med_records):
        """진료기록 포맷팅"""
        if not med_records:
            return "진료기록 없음"

        records = []
        for record in med_records[:3]:
            rec_str = ", ".join([f"{k}: {v}" for k, v in record.items() if pd.notna(v)])
            records.append(rec_str)

        return records if records else "진료기록 없음"

    def _format_lab_tests(self, lab_records):
        """진단검사 포맷팅"""
        if not lab_records:
            return []

        tests = []
        for record in lab_records[:10]:
            test_str = " | ".join([f"{k}: {v}" for k, v in record.items() if pd.notna(v)])
            if test_str:
                tests.append(test_str)

        return tests

    def _format_imaging(self, imaging_records):
        """영상검사 포맷팅"""
        if not imaging_records:
            return []

        images = []
        for record in imaging_records[:5]:
            img_str = " - ".join([str(v) for v in record.values() if pd.notna(v)])
            if img_str:
                images.append(img_str)

        return images

    def _format_functional_tests(self, func_records):
        """기능검사 포맷팅"""
        if not func_records:
            return []

        tests = []
        for record in func_records[:5]:
            test_str = " - ".join([str(v) for v in record.values() if pd.notna(v)])
            if test_str:
                tests.append(test_str)

        return tests

    def _format_initial_nursing(self, nursing_records):
        """초기간호기록 포맷팅"""
        if not nursing_records:
            return "초기간호기록 없음"

        records = []
        for record in nursing_records[:3]:
            rec_str = ", ".join([f"{k}: {v}" for k, v in record.items() if pd.notna(v)])
            records.append(rec_str)

        return records if records else "초기간호기록 없음"

    def extract_full_cycle_data(self, patient_ids):
        """
        전주기 Clinical Note용 추가 데이터를 추출합니다.
        (수혈+CP, 타과의뢰+의뢰서, 퇴실간호기록, 간호일지)

        Args:
            patient_ids (list): 환자 ID 리스트
        """
        for file_key, file_name in FULL_CYCLE_ADDITIONAL_FILES.items():
            file_path = os.path.join(self.data_path, file_name)

            try:
                df = pd.read_excel(file_path)

                # 각 환자에 대해 데이터 필터링
                for patient_id in patient_ids:
                    patient_records = df[df.iloc[:, 0] == patient_id]

                    if not patient_records.empty:
                        self.patient_data[patient_id][file_key] = patient_records.to_dict('records')
                    else:
                        self.patient_data[patient_id][file_key] = []

                print(f"[OK] {file_key} 로딩 완료 (전주기용)")

            except Exception as e:
                print(f"[FAIL] {file_key} 로딩 실패: {str(e)}")
                for patient_id in patient_ids:
                    if patient_id in self.patient_data:
                        self.patient_data[patient_id][file_key] = []

    def format_for_full_cycle_note(self, patient_id):
        """
        전주기 Clinical Note용으로 모든 데이터를 포맷팅합니다.

        Args:
            patient_id: 환자 ID

        Returns:
            dict: 전체 환자 정보 (13개 파일 데이터 포함)
        """
        if patient_id not in self.patient_data:
            raise ValueError(f"환자 ID {patient_id}의 데이터가 없습니다.")

        # 기본 포맷팅 데이터 가져오기
        formatted_data = self.format_for_clinical_note(patient_id)

        patient = self.patient_data[patient_id]

        # 전주기용 추가 데이터 포맷팅
        formatted_data["수혈_CP"] = self._format_transfusion(patient.get("3_수혈+CP", []))
        formatted_data["타과의뢰"] = self._format_consultation(patient.get("6_타과의뢰+의뢰서", []))
        formatted_data["퇴실간호기록"] = self._format_discharge_nursing(patient.get("11_퇴실간호기록", []))
        formatted_data["간호일지"] = self._format_nursing_notes(patient.get("12_간호일지", []))

        return formatted_data

    def _format_transfusion(self, transfusion_records):
        """수혈+CP 포맷팅"""
        if not transfusion_records:
            return "수혈/CP 기록 없음"

        records = []
        for record in transfusion_records:
            rec_str = " | ".join([f"{k}: {v}" for k, v in record.items() if pd.notna(v)])
            if rec_str:
                records.append(rec_str)

        return records if records else "수혈/CP 기록 없음"

    def _format_consultation(self, consultation_records):
        """타과의뢰+의뢰서 포맷팅"""
        if not consultation_records:
            return "타과의뢰 기록 없음"

        records = []
        for record in consultation_records:
            rec_str = " | ".join([f"{k}: {v}" for k, v in record.items() if pd.notna(v)])
            if rec_str:
                records.append(rec_str)

        return records if records else "타과의뢰 기록 없음"

    def _format_discharge_nursing(self, discharge_records):
        """퇴실간호기록 포맷팅"""
        if not discharge_records:
            return "퇴실간호기록 없음"

        records = []
        for record in discharge_records:
            rec_str = ", ".join([f"{k}: {v}" for k, v in record.items() if pd.notna(v)])
            if rec_str:
                records.append(rec_str)

        return records if records else "퇴실간호기록 없음"

    def _format_nursing_notes(self, nursing_records):
        """간호일지 포맷팅"""
        if not nursing_records:
            return "간호일지 없음"

        records = []
        for record in nursing_records[:10]:  # 최대 10개
            rec_str = ", ".join([f"{k}: {v}" for k, v in record.items() if pd.notna(v)])
            if rec_str:
                records.append(rec_str)

        return records if records else "간호일지 없음"


if __name__ == "__main__":
    # 테스트 실행
    extractor = PatientDataExtractor()
    patient_data = extractor.extract_all()

    # 결과 출력
    print("\n추출된 환자 ID:")
    for patient_id in patient_data.keys():
        print(f"  - {patient_id}")

    # 첫 번째 환자 데이터 포맷팅 테스트
    first_patient_id = list(patient_data.keys())[0]
    formatted = extractor.format_for_clinical_note(first_patient_id)

    print(f"\n{first_patient_id} 환자 포맷팅 결과:")
    print(formatted)
