import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';
import path from 'path';
import readline from 'readline';

// Configuración de carga de proto files
const PROTO_PATH_GREETER = path.join(__dirname, '../proto/greeter.proto');
const PROTO_PATH_CALCULATOR = path.join(__dirname, '../proto/calculator.proto');

const packageDefinitionOptions = {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
};

// Cargar las definiciones de proto
const greeterPackageDef = protoLoader.loadSync(PROTO_PATH_GREETER, packageDefinitionOptions);
const calculatorPackageDef = protoLoader.loadSync(PROTO_PATH_CALCULATOR, packageDefinitionOptions);

const greeterProto = grpc.loadPackageDefinition(greeterPackageDef) as any;
const calculatorProto = grpc.loadPackageDefinition(calculatorPackageDef) as any;

// Crear clientes
const SERVER_URL = process.env.SERVER_URL || 'localhost:50051';

const greeterClient = new greeterProto.greeter.Greeter(
  SERVER_URL,
  grpc.credentials.createInsecure()
);

const calculatorClient = new calculatorProto.calculator.Calculator(
  SERVER_URL,
  grpc.credentials.createInsecure()
);

// Interfaz de línea de comandos
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

// Funciones de ejemplo

function testSayHello() {
  console.log('\n--- Test: SayHello (Unary RPC) ---');
  greeterClient.sayHello(
    { name: 'Juan', language: 'es' },
    (error: any, response: any) => {
      if (error) {
        console.error('Error:', error);
        return;
      }
      console.log('Respuesta:', response.message);
      console.log('Timestamp:', new Date(response.timestamp).toLocaleString());
    }
  );
}

function testSayHelloStream() {
  console.log('\n--- Test: SayHelloStream (Server Streaming) ---');
  const call = greeterClient.sayHelloStream({ name: 'María', language: 'es' });

  call.on('data', (response: any) => {
    console.log('Mensaje recibido:', response.message);
  });

  call.on('end', () => {
    console.log('Stream finalizado');
  });

  call.on('error', (error: any) => {
    console.error('Error:', error);
  });
}

function testSayHelloChat() {
  console.log('\n--- Test: SayHelloChat (Bidirectional Streaming) ---');
  const call = greeterClient.sayHelloChat();

  // Recibir mensajes del servidor
  call.on('data', (response: any) => {
    console.log('Servidor responde:', response.message);
  });

  call.on('end', () => {
    console.log('Chat finalizado');
  });

  call.on('error', (error: any) => {
    console.error('Error:', error);
  });

  // Enviar varios mensajes
  const messages = [
    { name: 'Pedro', language: 'es' },
    { name: 'Peter', language: 'en' },
    { name: 'Pierre', language: 'fr' },
  ];

  messages.forEach((msg, index) => {
    setTimeout(() => {
      console.log('Enviando:', msg.name);
      call.write(msg);

      if (index === messages.length - 1) {
        setTimeout(() => call.end(), 1000);
      }
    }, index * 2000);
  });
}

function testCalculator() {
  console.log('\n--- Test: Calculator ---');

  // Suma
  calculatorClient.add({ num1: 10, num2: 5 }, (error: any, response: any) => {
    if (error) {
      console.error('Error:', error);
      return;
    }
    console.log('10 + 5 =', response.result);
  });

  // Resta
  calculatorClient.subtract({ num1: 10, num2: 5 }, (error: any, response: any) => {
    if (error) {
      console.error('Error:', error);
      return;
    }
    console.log('10 - 5 =', response.result);
  });

  // Multiplicación
  calculatorClient.multiply({ num1: 10, num2: 5 }, (error: any, response: any) => {
    if (error) {
      console.error('Error:', error);
      return;
    }
    console.log('10 × 5 =', response.result);
  });

  // División
  calculatorClient.divide({ num1: 10, num2: 5 }, (error: any, response: any) => {
    if (error) {
      console.error('Error:', error);
      return;
    }
    console.log('10 ÷ 5 =', response.result);
  });

  // División por cero
  calculatorClient.divide({ num1: 10, num2: 0 }, (error: any, response: any) => {
    if (error) {
      console.error('Error:', error);
      return;
    }
    if (response.error) {
      console.log('10 ÷ 0 = Error:', response.error);
    }
  });
}

function testSumStream() {
  console.log('\n--- Test: SumStream (Client Streaming) ---');
  const call = calculatorClient.sumStream((error: any, response: any) => {
    if (error) {
      console.error('Error:', error);
      return;
    }
    console.log('Suma total:', response.result);
  });

  const numbers = [10, 20, 30, 40, 50];

  numbers.forEach((num, index) => {
    setTimeout(() => {
      console.log('Enviando:', num);
      call.write({ value: num });

      if (index === numbers.length - 1) {
        call.end();
      }
    }, index * 500);
  });
}

// Menú interactivo
function showMenu() {
  console.log('\n=== Cliente gRPC - Menú de Pruebas ===');
  console.log('1. SayHello (Unary RPC)');
  console.log('2. SayHelloStream (Server Streaming)');
  console.log('3. SayHelloChat (Bidirectional Streaming)');
  console.log('4. Calculator (Operaciones básicas)');
  console.log('5. SumStream (Client Streaming)');
  console.log('6. Ejecutar todos los tests');
  console.log('0. Salir');
  console.log('\nConectado a:', SERVER_URL);

  rl.question('\nSelecciona una opción: ', (answer) => {
    switch (answer.trim()) {
      case '1':
        testSayHello();
        setTimeout(showMenu, 2000);
        break;
      case '2':
        testSayHelloStream();
        setTimeout(showMenu, 7000);
        break;
      case '3':
        testSayHelloChat();
        setTimeout(showMenu, 10000);
        break;
      case '4':
        testCalculator();
        setTimeout(showMenu, 2000);
        break;
      case '5':
        testSumStream();
        setTimeout(showMenu, 5000);
        break;
      case '6':
        testSayHello();
        setTimeout(() => testSayHelloStream(), 2000);
        setTimeout(() => testCalculator(), 9000);
        setTimeout(() => testSumStream(), 11000);
        setTimeout(showMenu, 18000);
        break;
      case '0':
        console.log('\nCerrando cliente...');
        rl.close();
        process.exit(0);
        break;
      default:
        console.log('\nOpción no válida');
        setTimeout(showMenu, 1000);
    }
  });
}

// Iniciar el menú
console.log('\n🚀 Cliente gRPC iniciado');
showMenu();
