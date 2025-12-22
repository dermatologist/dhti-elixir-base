"""
Copyright 2025 Bell Eapen

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from ..cds_hook.card import CDSHookCard


def add_card(output: str | CDSHookCard, cards: list | None = None) -> dict:
    """Add a CDSHookCard to the output list."""
    if cards is None:
        cards = []
    if isinstance(output, CDSHookCard):
        cards.append(output)
    elif isinstance(output, str):
        cards.append(CDSHookCard(summary=output))
    else:
        raise ValueError("Output must be a string or CDSHookCard")
    return {"cards": cards}

def get_card(output: str | CDSHookCard) -> dict:
    """Get a CDSHookCard as a dictionary."""
    if isinstance(output, CDSHookCard):
        return output.model_dump()
    elif isinstance(output, str):
        return {"cards": [CDSHookCard(summary=output).model_dump()]}
    else:
        raise ValueError("Output must be a string or CDSHookCard")
