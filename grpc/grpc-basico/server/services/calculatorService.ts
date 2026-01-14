import * as grpc from '@grpc/grpc-js';

export const calculatorService = {
  // Suma
  add: (call: any, callback: any) => {
    const { num1, num2 } = call.request;
    console.log(`➕ Add: ${num1} + ${num2}`);

    callback(null, {
      result: num1 + num2,
      error: '',
    });
  },

  // Resta
  subtract: (call: any, callback: any) => {
    const { num1, num2 } = call.request;
    console.log(`➖ Subtract: ${num1} - ${num2}`);

    callback(null, {
      result: num1 - num2,
      error: '',
    });
  },

  // Multiplicación
  multiply: (call: any, callback: any) => {
    const { num1, num2 } = call.request;
    console.log(`✖️  Multiply: ${num1} × ${num2}`);

    callback(null, {
      result: num1 * num2,
      error: '',
    });
  },

  // División
  divide: (call: any, callback: any) => {
    const { num1, num2 } = call.request;
    console.log(`➗ Divide: ${num1} ÷ ${num2}`);

    if (num2 === 0) {
      callback(null, {
        result: 0,
        error: 'No se puede dividir por cero',
      });
      return;
    }

    callback(null, {
      result: num1 / num2,
      error: '',
    });
  },

  // Client Streaming: Suma múltiples números
  sumStream: (call: any, callback: any) => {
    console.log('📨 SumStream iniciado (client streaming)');
    let sum = 0;
    let count = 0;

    call.on('data', (request: any) => {
      const { value } = request;
      sum += value;
      count++;
      console.log(`  💬 Número recibido: ${value} (suma acumulada: ${sum})`);
    });

    call.on('end', () => {
      console.log(`  ✅ Stream finalizado. Total de ${count} números sumados`);
      callback(null, {
        result: sum,
        error: '',
      });
    });

    call.on('error', (error: Error) => {
      console.error('  ❌ Error en stream:', error);
      callback(error, null);
    });
  },
};
