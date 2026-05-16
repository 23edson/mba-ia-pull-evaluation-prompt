"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core import messages
from langchain_core import messages
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_NAME = "bug_to_user_story_v2"



def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).
    """
    try:
        # Cria o ChatPromptTemplate a partir do YAML
        system_prompt = prompt_data.get("system_prompt", "")
        messages = prompt_data.get("messages", [])

        chat_messages = []
        if system_prompt:
            chat_messages.append(("system", system_prompt))

        user_prompt = prompt_data.get("user_prompt", "")
        if user_prompt:
            chat_messages.append(("user", user_prompt))

        for m in messages:
            chat_messages.append((m["role"], m["content"]))

        prompt = ChatPromptTemplate.from_messages(chat_messages)

        # Tags descritivas do domínio e propósito
        tags = prompt_data.get("tags") or [
            "bug-analysis",
            "user-story",
            "product-management",
            "optimized",
        ]

        # Técnicas aplicadas separadas das tags
        techniques_used = prompt_data.get("techniques_applied") or [
            "role_prompting",
            "few_shot_learning",
            "skeleton_of_thought",
        ]

        description = prompt_data.get(
            "description",
            "Prompt otimizado para conversão de bug reports em user stories"
        )

        print(f"  Tags: {tags}")
        print(f"  Técnicas: {techniques_used}")
        print(f"  Descrição: {description}")

        # Faz push público
        hub.push(
            prompt_name,
            prompt,
            new_repo_is_public=True,
            tags=tags,
        )
        print(f"Prompt '{prompt_name}' publicado com sucesso no LangSmith Hub!")
        return True
    except Exception as e:
        print(f"Erro ao fazer push do prompt: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).
    """
    errors = []
    if not isinstance(prompt_data, dict):
        errors.append("Prompt não é um dicionário.")
        return False, errors
    if not prompt_data.get("messages") and not prompt_data.get("system_prompt"):
        errors.append("Prompt deve ter pelo menos 'messages' ou 'system_prompt'.")
    if not prompt_data.get("input_variables"):
        errors.append("Campo 'input_variables' ausente.")
    return (len(errors) == 0), errors


def main():
    # Config
    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        print("Configure as variáveis de ambiente no .env.")
        return 1

    prompt_file = "prompts/bug_to_user_story_v2.yml"
    username = os.environ.get("USERNAME_LANGSMITH_HUB") or "seu_username"
    prompt_name = f"{username}/{PROMPT_NAME}"

    # Lê YAML
    prompt_data = load_yaml(prompt_file)
    if not prompt_data:
        print(f"Falha ao carregar {prompt_file}")
        return 1

    # Corrige para YAML com chave de nível superior
    if isinstance(prompt_data, dict) and len(prompt_data) == 1:
        only_key = next(iter(prompt_data))
        prompt_data = prompt_data[only_key]

    # Valida
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("Erros de validação:")
        for err in errors:
            print(f"- {err}")
        return 1

    # Push
    if push_prompt_to_langsmith(prompt_name, prompt_data):
        print("Push realizado com sucesso!")
        return 0
    else:
        print("Falha ao fazer push do prompt.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
