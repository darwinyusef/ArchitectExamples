import * as grpc from '@grpc/grpc-js';

// Traducciones para diferentes idiomas
const greetings: Record<string, string> = {
  es: 'Hola',
  en: 'Hello',
  fr: 'Bonjour',
  de: 'Hallo',
  it: 'Ciao',
};

export const greeterService = {
  // RPC Unario: Una petición, una respuesta
  sayHello: (call: any, callback: any) => {
    const { name, language } = call.request;
    const greeting = greetings[language] || greetings.en;

    console.log(`📨 SayHello recibido: name="${name}", language="${language}"`);

    const response = {
      message: `${greeting}, ${name}!`,
      timestamp: Date.now(),
    };

    callback(null, response);
  },

  // Server Streaming: Una petición, múltiples respuestas
  sayHelloStream: (call: any) => {
    const { name, language } = call.request;
    const greeting = greetings[language] || greetings.en;

    console.log(`📨 SayHelloStream recibido: name="${name}", language="${language}"`);

    // Enviar 5 saludos en secuencia
    const messages = [
      `${greeting}, ${name}!`,
      `¿Cómo estás, ${name}?`,
      `Bienvenido/a al tutorial de gRPC`,
      `Este es un ejemplo de Server Streaming`,
      `¡Hasta pronto, ${name}!`,
    ];

    messages.forEach((message, index) => {
      setTimeout(() => {
        call.write({
          message,
          timestamp: Date.now(),
        });

        // Terminar el stream después del último mensaje
        if (index === messages.length - 1) {
          call.end();
        }
      }, index * 1000); // Enviar cada segundo
    });
  },

  // Bidirectional Streaming: Múltiples peticiones, múltiples respuestas
  sayHelloChat: (call: any) => {
    console.log('📨 SayHelloChat iniciado (bidirectional streaming)');

    call.on('data', (request: any) => {
      const { name, language } = request;
      const greeting = greetings[language] || greetings.en;

      console.log(`  💬 Mensaje recibido: name="${name}", language="${language}"`);

      // Responder inmediatamente a cada mensaje
      call.write({
        message: `${greeting}, ${name}! (Mensaje recibido)`,
        timestamp: Date.now(),
      });
    });

    call.on('end', () => {
      console.log('  ✅ Chat finalizado');
      call.end();
    });

    call.on('error', (error: Error) => {
      console.error('  ❌ Error en chat:', error);
    });
  },
};
