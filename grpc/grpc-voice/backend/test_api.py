#!/usr/bin/env python3
"""
Script de prueba para la API de transcripción

Prueba la conexión y funcionalidad del servidor.
"""

import asyncio
import httpx
from pathlib import Path


async def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8001/health")

            if response.status_code == 200:
                print("✅ Health check passed")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Health check failed: {response.status_code}")

        except httpx.ConnectError:
            print("❌ Cannot connect to server. Is it running?")
            return False

    return True


async def test_root():
    """Test root endpoint"""
    print("\n🔍 Testing root endpoint...")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8001/")

            if response.status_code == 200:
                print("✅ Root endpoint working")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Root endpoint failed: {response.status_code}")

        except httpx.ConnectError:
            print("❌ Cannot connect to server")
            return False

    return True


async def test_transcribe_with_file(audio_file: str = None):
    """Test transcribe endpoint with audio file"""

    if not audio_file:
        print("\n⚠️  No audio file provided. Skipping transcription test.")
        print("   To test transcription, run:")
        print("   python test_api.py path/to/audio.mp3")
        return

    audio_path = Path(audio_file)

    if not audio_path.exists():
        print(f"\n❌ Audio file not found: {audio_file}")
        return

    print(f"\n🔍 Testing transcription with: {audio_file}")

    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            with open(audio_path, 'rb') as f:
                files = {'file': f}
                data = {'language': 'es'}

                print("   Uploading and transcribing... (this may take a while)")
                response = await client.post(
                    "http://localhost:8001/transcribe",
                    files=files,
                    data=data
                )

                if response.status_code == 200:
                    result = response.json()
                    print("✅ Transcription successful!")
                    print(f"   Text: {result.get('transcription', 'N/A')}")
                    print(f"   Language: {result.get('language', 'N/A')}")
                    print(f"   Duration: {result.get('duration', 0):.2f}s")
                    print(f"   Words: {result.get('words_count', 0)}")
                else:
                    print(f"❌ Transcription failed: {response.status_code}")
                    print(f"   Error: {response.text}")

        except httpx.ConnectError:
            print("❌ Cannot connect to server")
        except Exception as e:
            print(f"❌ Error: {e}")


async def main():
    """Run all tests"""
    import sys

    print("=" * 60)
    print("🧪 Testing gRPC Voice API")
    print("=" * 60)

    # Test health
    if not await test_health():
        print("\n❌ Server is not running. Please start it first:")
        print("   cd backend && python main.py")
        return

    # Test root
    await test_root()

    # Test transcription if file provided
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        await test_transcribe_with_file(audio_file)
    else:
        await test_transcribe_with_file()

    print("\n" + "=" * 60)
    print("✅ Tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
