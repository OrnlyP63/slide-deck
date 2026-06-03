from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CompileResult:
    success: bool
    tex_path: Path
    log: str
    pdf_path: Path | None = None
    cached: bool = False
    errors: list[str] = field(default_factory=list)


class Compiler:
    def __init__(self, output_dir: Path, engine: str = "pdflatex") -> None:
        self.output_dir = output_dir
        self.engine = engine
        self._cache_dir = output_dir / ".cache"

    def compile(self, tex_content: str, output_name: str) -> CompileResult:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._cache_dir.mkdir(exist_ok=True)

        content_hash = hashlib.sha256(tex_content.encode()).hexdigest()
        hash_file = self._cache_dir / f"{output_name}.hash"
        tex_path = self.output_dir / f"{output_name}.tex"
        pdf_path = self.output_dir / f"{output_name}.pdf"

        if hash_file.exists() and hash_file.read_text().strip() == content_hash and pdf_path.exists():
            return CompileResult(success=True, tex_path=tex_path, pdf_path=pdf_path, log="", cached=True)

        tex_path.write_text(tex_content, encoding="utf-8")

        log = ""
        success = True
        for _ in range(2):
            rc, output = self._run(tex_path)
            log += output
            if rc != 0:
                success = False
                break

        if success:
            hash_file.write_text(content_hash)
            return CompileResult(success=True, tex_path=tex_path, pdf_path=pdf_path, log=log)

        return CompileResult(
            success=False,
            tex_path=tex_path,
            log=log,
            errors=self._parse_errors(log),
        )

    def _run(self, tex_path: Path) -> tuple[int, str]:
        result = subprocess.run(
            [self.engine, "-interaction=nonstopmode", "-output-directory", str(self.output_dir), str(tex_path)],
            capture_output=True,
            text=True,
        )
        return result.returncode, result.stdout + result.stderr

    @staticmethod
    def _parse_errors(log: str) -> list[str]:
        return [line for line in log.splitlines() if line.startswith("!")]
