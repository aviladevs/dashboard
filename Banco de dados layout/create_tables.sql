-- Scripts de criação de tabelas para Azure SQL Database
-- Dashboard Ávila Transportes

-- Tabela principal de fretes e transportes
CREATE TABLE fretes (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    data_emissao DATE NOT NULL,
    numero NVARCHAR(50),
    pagador_nome NVARCHAR(255),
    valor_frete DECIMAL(10,2),
    notas_fiscais NVARCHAR(100),
    remetente_nome NVARCHAR(255),
    remetente_cidade NVARCHAR(100),
    destinatario_nome NVARCHAR(255),
    destinatario_cidade NVARCHAR(100),
    soma_volumes INT,
    soma_notas DECIMAL(10,2),
    soma_pesos DECIMAL(10,3),
    data_criacao DATETIME2 DEFAULT GETDATE(),
    data_atualizacao DATETIME2 DEFAULT GETDATE()
);

-- Tabela de transações financeiras
CREATE TABLE transacoes_financeiras (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    data_transacao DATE NOT NULL,
    descricao NVARCHAR(500),
    valor DECIMAL(10,2) NOT NULL,
    tipo NVARCHAR(50) CHECK (tipo IN ('Receita', 'Despesa')),
    categoria NVARCHAR(100),
    setor NVARCHAR(100),
    centro_custo NVARCHAR(100),
    id_transacao_externa NVARCHAR(100) UNIQUE,
    conciliado_com NVARCHAR(100),
    data_criacao DATETIME2 DEFAULT GETDATE(),
    data_atualizacao DATETIME2 DEFAULT GETDATE()
);

-- Tabela de conciliações
CREATE TABLE conciliacoes (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    id_frete BIGINT,
    id_transacao BIGINT,
    tipo_conciliacao NVARCHAR(50),
    observacoes NVARCHAR(500),
    usuario_conciliacao NVARCHAR(100),
    data_conciliacao DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (id_frete) REFERENCES fretes(id),
    FOREIGN KEY (id_transacao) REFERENCES transacoes_financeiras(id)
);

-- Tabela de configurações do sistema
CREATE TABLE configuracoes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    chave NVARCHAR(100) NOT NULL UNIQUE,
    valor NVARCHAR(500),
    descricao NVARCHAR(255),
    data_criacao DATETIME2 DEFAULT GETDATE(),
    data_atualizacao DATETIME2 DEFAULT GETDATE()
);

-- Índices para melhor performance
CREATE INDEX IX_fretes_data_emissao ON fretes(data_emissao);
CREATE INDEX IX_fretes_pagador ON fretes(pagador_nome);
CREATE INDEX IX_fretes_destinatario_cidade ON fretes(destinatario_cidade);

CREATE INDEX IX_transacoes_data ON transacoes_financeiras(data_transacao);
CREATE INDEX IX_transacoes_tipo ON transacoes_financeiras(tipo);
CREATE INDEX IX_transacoes_categoria ON transacoes_financeiras(categoria);
CREATE INDEX IX_transacoes_id_externa ON transacoes_financeiras(id_transacao_externa);

-- Inserir configurações padrão
INSERT INTO configuracoes (chave, valor, descricao) VALUES
('versao_schema', '1.0', 'Versão do schema do banco de dados'),
('migrado_csv', 'false', 'Indica se os dados CSV foram migrados'),
('backup_automatico', 'true', 'Habilita backup automático');

-- Trigger para atualizar data_atualizacao automaticamente
-- Para tabela fretes
CREATE TRIGGER tr_fretes_update
ON fretes
AFTER UPDATE
AS
BEGIN
    UPDATE fretes 
    SET data_atualizacao = GETDATE()
    WHERE id IN (SELECT id FROM inserted);
END;

-- Para tabela transacoes_financeiras
CREATE TRIGGER tr_transacoes_update
ON transacoes_financeiras
AFTER UPDATE
AS
BEGIN
    UPDATE transacoes_financeiras 
    SET data_atualizacao = GETDATE()
    WHERE id IN (SELECT id FROM inserted);
END;