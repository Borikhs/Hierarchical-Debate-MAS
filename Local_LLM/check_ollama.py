# -*- coding: utf-8 -*-
"""
Ollama 설치 및 Llama 3.1 8B 모델 확인 스크립트
"""

import subprocess
import requests
import sys
import time

def print_header(text):
    """헤더 출력"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)

def check_ollama_installed():
    """Ollama가 설치되어 있는지 확인"""
    print_header("1. Ollama 설치 확인")
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"[OK] Ollama가 설치되어 있습니다!")
            print(f"     버전: {version}")
            return True
        else:
            print("[FAIL] Ollama가 설치되어 있지 않습니다.")
            print("\n설치 방법:")
            print("  1. https://ollama.com/download/windows 접속")
            print("  2. OllamaSetup.exe 다운로드 및 설치")
            print("  또는 OLLAMA_INSTALLATION_GUIDE.md 참조")
            return False
    except FileNotFoundError:
        print("[FAIL] Ollama가 설치되어 있지 않습니다.")
        print("\n설치 방법:")
        print("  1. https://ollama.com/download/windows 접속")
        print("  2. OllamaSetup.exe 다운로드 및 설치")
        print("  또는 OLLAMA_INSTALLATION_GUIDE.md 참조")
        return False
    except Exception as e:
        print(f"[ERROR] 확인 중 오류 발생: {str(e)}")
        return False

def check_ollama_server():
    """Ollama 서버가 실행 중인지 확인"""
    print_header("2. Ollama 서버 상태 확인")
    try:
        response = requests.get("http://localhost:11434", timeout=5)
        if response.status_code == 200:
            print("[OK] Ollama 서버가 실행 중입니다!")
            print(f"     URL: http://localhost:11434")
            return True
        else:
            print(f"[WARN] Ollama 서버 응답 이상: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[FAIL] Ollama 서버에 연결할 수 없습니다.")
        print("\n서버 시작 방법:")
        print("  명령 프롬프트에서: ollama serve")
        print("  또는 Ollama가 백그라운드에서 자동 실행됩니다.")
        return False
    except Exception as e:
        print(f"[ERROR] 확인 중 오류 발생: {str(e)}")
        return False

def check_llama_model():
    """Llama 3.1 8B 모델이 다운로드되어 있는지 확인"""
    print_header("3. Llama 3.1 8B 모델 확인")
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            output = result.stdout
            if "llama3.1:8b" in output.lower():
                print("[OK] Llama 3.1 8B 모델이 설치되어 있습니다!")
                print("\n설치된 모델 목록:")
                print(output)
                return True
            else:
                print("[FAIL] Llama 3.1 8B 모델이 설치되어 있지 않습니다.")
                print("\n모델 다운로드 방법:")
                print("  ollama pull llama3.1:8b")
                print("\n설치된 모델 목록:")
                print(output if output.strip() else "  (없음)")
                return False
        else:
            print(f"[ERROR] ollama list 실행 실패: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] 확인 중 오류 발생: {str(e)}")
        return False

def test_llama_model():
    """Llama 3.1 8B 모델 간단 테스트"""
    print_header("4. Llama 3.1 8B 모델 테스트")
    print("간단한 테스트 메시지를 전송합니다...\n")

    try:
        # Ollama API를 통한 테스트
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.1:8b",
                "prompt": "Say hello in Korean.",
                "stream": False
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            generated_text = result.get("response", "")
            print("[OK] 모델 테스트 성공!")
            print(f"\n질문: Say hello in Korean.")
            print(f"응답: {generated_text}\n")
            return True
        else:
            print(f"[FAIL] 모델 테스트 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("[WARN] 응답 시간 초과 (30초)")
        print("모델이 처음 로딩되는 경우 시간이 걸릴 수 있습니다.")
        return False
    except Exception as e:
        print(f"[ERROR] 테스트 중 오류 발생: {str(e)}")
        return False

def main():
    """메인 실행 함수"""
    print("\n" + "=" * 60)
    print("Ollama & Llama 3.1 8B 설치 확인 도구")
    print("=" * 60)

    results = {
        "ollama_installed": False,
        "server_running": False,
        "model_downloaded": False,
        "model_working": False
    }

    # 1. Ollama 설치 확인
    results["ollama_installed"] = check_ollama_installed()
    if not results["ollama_installed"]:
        print("\n" + "=" * 60)
        print("[종료] Ollama를 먼저 설치해주세요.")
        print("=" * 60)
        return

    time.sleep(1)

    # 2. Ollama 서버 확인
    results["server_running"] = check_ollama_server()
    if not results["server_running"]:
        print("\n[INFO] 서버를 시작하는 중...")
        # 서버 자동 시작 시도
        try:
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("[INFO] 5초 대기 중...")
            time.sleep(5)
            results["server_running"] = check_ollama_server()
        except:
            pass

    if not results["server_running"]:
        print("\n[WARN] 서버 시작 실패")
        print("수동으로 'ollama serve'를 실행해주세요.")

    time.sleep(1)

    # 3. Llama 3.1 8B 모델 확인
    if results["ollama_installed"]:
        results["model_downloaded"] = check_llama_model()
        if not results["model_downloaded"]:
            print("\n[INFO] Llama 3.1 8B 모델을 다운로드하시겠습니까?")
            print("모델 크기: 약 4.7GB, 소요 시간: 5-15분")
            user_input = input("다운로드 (y/n)? ").strip().lower()

            if user_input == 'y':
                print("\n모델 다운로드 시작...")
                try:
                    result = subprocess.run(
                        ["ollama", "pull", "llama3.1:8b"],
                        timeout=1800  # 30분
                    )
                    if result.returncode == 0:
                        results["model_downloaded"] = True
                        print("\n[OK] 모델 다운로드 완료!")
                    else:
                        print("\n[FAIL] 모델 다운로드 실패")
                except subprocess.TimeoutExpired:
                    print("\n[FAIL] 다운로드 시간 초과 (30분)")
                except Exception as e:
                    print(f"\n[ERROR] 다운로드 중 오류: {str(e)}")

    time.sleep(1)

    # 4. 모델 테스트
    if results["server_running"] and results["model_downloaded"]:
        results["model_working"] = test_llama_model()

    # 최종 결과
    print_header("설치 확인 결과 요약")
    print(f"1. Ollama 설치:       {'✓' if results['ollama_installed'] else '✗'}")
    print(f"2. 서버 실행:         {'✓' if results['server_running'] else '✗'}")
    print(f"3. Llama 3.1 8B:      {'✓' if results['model_downloaded'] else '✗'}")
    print(f"4. 모델 작동:         {'✓' if results['model_working'] else '✗'}")

    if all(results.values()):
        print("\n" + "=" * 60)
        print("[성공] 모든 준비가 완료되었습니다!")
        print("=" * 60)
        print("\nAdmin Agent Local 실행:")
        print("  cd Admin_Agent_Local/scripts")
        print("  python admin_agent_local.py")
    else:
        print("\n" + "=" * 60)
        print("[실패] 일부 항목이 완료되지 않았습니다.")
        print("=" * 60)
        print("\nOLLAMA_INSTALLATION_GUIDE.md를 참조하세요.")

if __name__ == "__main__":
    main()
