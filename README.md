***English:***

I built this project to simulate a real-world bank operating directly in the terminal, with a strong focus on security and data consistency. Using SQLite3, I implemented constraints that instantly block invalid CPF registrations and prevent accounts from going into a negative balance. The main technical highlight is how Pix transfers are handled using manual transactions (commit and rollback). This guarantees that if there is any system failure or power outage mid-operation, the database automatically rolls back everything so no money vanishes into thin air. Additionally, the code is 100% protected against SQL Injection attacks through the use of parameterized queries.

______________________________

***Português:***

Criei este projeto para simular um banco real direto no terminal, focando em segurança e consistência de dados. Usei o SQLite3 para criar regras que barram cadastros com CPFs inválidos e impedem que o saldo fique negativo. O maior destaque técnico foi o controle de transferências via Pix utilizando transações manuais (commit e rollback). Isso garante que, se houver qualquer falha ou queda de energia no meio da operação, o banco desfaz tudo automaticamente para o dinheiro não sumir. Além disso, o código está 100% protegido contra ataques de SQL Injection através de queries parametrizadas.
