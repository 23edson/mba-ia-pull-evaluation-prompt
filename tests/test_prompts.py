"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

class TestPrompts:

    @pytest.fixture
    def prompt_data(self):
        """Fixture para carregar os dados do prompt v2."""
        file_path = (
            Path(__file__).parent.parent
            / "prompts"
            / "bug_to_user_story_v2.yml"
        )

        data = load_prompts(str(file_path))

        # Permite tanto:
        # bug_to_user_story_v2:
        #   ...
        #
        # quanto:
        # system_prompt: ...
        return data.get("bug_to_user_story_v2", data)

    def test_prompt_has_system_prompt(self, prompt_data):
        """
        Verifica se o campo 'system_prompt' existe
        e possui conteúdo válido.
        """
        system_prompt = prompt_data.get("system_prompt", "")

        assert isinstance(system_prompt, str)
        assert len(system_prompt.strip()) > 0

    def test_prompt_has_role_definition(self, prompt_data):
        """
        Verifica se o prompt define uma persona/role.
        """

        system_prompt = prompt_data.get("system_prompt", "").lower()

        role_keywords = [
            "você é",
            "assistente especializado",
            "especialista",
            "product owner",
            "product manager",
            "atuar como",
        ]

        assert any(
            keyword in system_prompt
            for keyword in role_keywords
        )

    def test_prompt_mentions_format(self, prompt_data):
        """
        Verifica se o prompt define
        uma estrutura/formato de resposta.
        """

        system_prompt = prompt_data.get("system_prompt", "").lower()

        format_keywords = [
            "user story",
            "template",
            "critérios de aceitação",
            "dado que",
            "quando",
            "então",
            "estrutura",
        ]

        assert any(
            keyword in system_prompt
            for keyword in format_keywords
        )

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """
        Verifica se o prompt contém exemplos
        de entrada/saída (Few-shot Learning).
        """

        system_prompt = prompt_data.get("system_prompt", "").lower()

        has_input_output = (
            "input:" in system_prompt
            and "output:" in system_prompt
        )

        has_entrada_saida = (
            "entrada:" in system_prompt
            and "saída:" in system_prompt
        )

        assert has_input_output or has_entrada_saida

    def test_prompt_no_todos(self, prompt_data):
        """
        Garante que não existam marcações TODO
        esquecidas no prompt.
        """

        system_prompt = prompt_data.get("system_prompt", "").upper()

        assert "[TODO]" not in system_prompt
        assert "TODO:" not in system_prompt

    def test_minimum_techniques(self, prompt_data):
        """
        Verifica se pelo menos duas técnicas
        de prompt engineering foram declaradas.
        """

        techniques = prompt_data.get("techniques_applied", [])

        valid_techniques = {
            "Few-shot Learning",
            "Role Prompting",
            "Chain of Thought",
            "Skeleton of Thought",
            "Structured Output",
            "Conditional Routing",
            "Literal Copying",
            "Anchored Structure",
        }

        assert isinstance(techniques, list)
        assert len(techniques) >= 2

        assert any(
            valid.lower() in technique.lower()
            for technique in techniques
            for valid in valid_techniques
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])