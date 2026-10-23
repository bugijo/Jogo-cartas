# Decisões técnicas e riscos

- O kit 0.2 continua íntegro. A evolução é opt-in e não deve ser impressa como jogo completo.
- IDs dos dez protagonistas foram reaproveitados para rastreabilidade. A identidade e profissão vêm do catálogo anterior; nenhuma habilidade antiga foi alterada.
- O PRNG de Python recebe semente explícita. O arquivo de salvamento guarda estado de heróis e acampamento, mas ainda não guarda o estado interno do PRNG, inventários, mapas ou missões; portanto **não garante retomada idêntica da campanha**.
- O ensaio agregado possui cinco ataques e cinco refeições por execução. Não estima vitórias, mortalidade ou tempo de mesa.
- A ausência de artes e PDFs novos é deliberada enquanto geometria, componentes e paginação da nova escala não estiverem especificados e validados.
