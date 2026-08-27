def extract_video(path):
    """
    Extract speech from a video/audio file.

    Requires faster-whisper.

    The model runs locally.
    """

    try:

        from faster_whisper import WhisperModel

    except ImportError:

        raise RuntimeError(
            "Video transcription requires faster-whisper."
        )

    model = WhisperModel(
        "small",
        device="cpu",
        compute_type="int8"
    )

    segments, _ = model.transcribe(
        str(path)
    )

    results = []

    for segment in segments:

        text = segment.text.strip()

        if not text:
            continue

        results.append(
            {
                "text": text,
                "page": None,
                "location": (
                    f"{segment.start:.1f}s - "
                    f"{segment.end:.1f}s"
                ),
            }
        )

    return results