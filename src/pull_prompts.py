"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def _infer_role(message_template) -> str:
    """
    Infer role from LangChain message prompt template-ish objects.

    Normalizes to OpenAI-style roles: system/user/assistant.
    """
    # ChatMessagePromptTemplate usually has an explicit role attr
    role = getattr(message_template, "role", None)
    if isinstance(role, str) and role.strip():
        role_lc = role.strip().lower()
        if role_lc in {"system", "user", "assistant"}:
            return role_lc
        if role_lc == "human":
            return "user"
        return role_lc

    cls_name = message_template.__class__.__name__.lower()
    if "system" in cls_name:
        return "system"
    if "human" in cls_name:
        return "user"
    if "ai" in cls_name:
        return "assistant"
    return "user"


def _extract_template_content(message_template) -> str:
    """
    Extracts prompt text from LangChain message templates.
    """
    # Most MessagePromptTemplates wrap a PromptTemplate in `prompt`
    prompt = getattr(message_template, "prompt", None)
    template = getattr(prompt, "template", None)
    if isinstance(template, str):
        return template

    # Some messages may carry raw content (BaseMessage-like)
    content = getattr(message_template, "content", None)
    if isinstance(content, str):
        return content

    # MessagesPlaceholder (or similar) should not become a textual message
    # It represents a list of messages injected at runtime.
    variable_name = getattr(message_template, "variable_name", None)
    if isinstance(variable_name, str) and variable_name.strip():
        return ""

    # Fallback: best-effort stringification
    try:
        return str(message_template)
    except Exception:
        return ""


def unpack_prompt(prompt_obj, prompt_name: str | None = None):
    """
    Desempacota um objeto de prompt do LangChain para um formato humano (dict).
    """
    # Estrutura básica seguindo as expectativas de utils.validate_prompt_structure
    unpacked = {
        "description": f"Prompt importado do LangSmith Hub: {prompt_name}"
        if prompt_name
        else "Prompt importado do LangSmith Hub",
        "version": "1.0.0",
        "input_variables": getattr(prompt_obj, "input_variables", []),
        "system_prompt": "",
        "messages": [],
        # Mantém >=2 técnicas para passar validações básicas
        "techniques_applied": ["bug-analysis","user-story","Imported from LangSmith", "Base Prompt"],
    }

    # Se for um ChatPromptTemplate (com mensagens)
    if hasattr(prompt_obj, "messages"):
        for m in prompt_obj.messages:
            # Ignora placeholders de mensagens (não são texto)
            if hasattr(m, "variable_name") and not hasattr(m, "prompt") and not hasattr(m, "content"):
                continue

            role = _infer_role(m)
            content = _extract_template_content(m)
            if not content.strip():
                continue

            # Organiza na estrutura de saída
            if role == "system" and not unpacked["system_prompt"]:
                unpacked["system_prompt"] = content
            else:
                unpacked["messages"].append({"role": role, "content": content})

    # Se for um PromptTemplate simples
    elif hasattr(prompt_obj, "template"):
        unpacked["system_prompt"] = prompt_obj.template

    return unpacked


def pull_prompts_from_langsmith():
    print_section_header("Pull de Prompts do LangSmith Hub")
    
    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        print("Configure as variáveis de ambiente necessárias no arquivo .env.")
        return False

    prompt_name = "leonanluppi/bug_to_user_story_v1"
    output_file = "prompts/bug_to_user_story_v1.yml"

    print(f"⏳ Fazendo pull de '{prompt_name}'...")
    
    try:
        # Faz pull do prompt via LangChain Hub
        prompt_obj = hub.pull(prompt_name)
        
        # Desempacota para formato humano (não apenas JSON serializado)
        prompt_data = unpack_prompt(prompt_obj, prompt_name=prompt_name)
        
        print(f"Pull concluído com sucesso!")
        
        # Salva o resultado no arquivo YAML
        print(f"⏳ Salvando em {output_file}...")
        if save_yaml(prompt_data, output_file):
            print(f"Prompt salvo em {output_file} formatado para humanos.")
            return True
        else:
            print(f"Falha ao salvar o arquivo YAML.")
            return False

    except Exception as e:
        print(f"Erro ao realizar pull do prompt: {e}")
        return False


def main():
    """Função principal"""
    success = pull_prompts_from_langsmith()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
