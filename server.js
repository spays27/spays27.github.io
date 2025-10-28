const fs = require('fs');
const path = require('path');
const http = require('http');

const PORT = process.env.PORT || 3000;
const registrosPath = path.join(__dirname, 'registros.jsonl');

// Asegura que exista el archivo
try { fs.closeSync(fs.openSync(registrosPath, 'a')); } catch (e) { console.error('No se pudo crear registros:', e); process.exit(1); }

const server = http.createServer((req, res) => {
  // Servir archivos estáticos simples
  if (req.method === 'GET') {
    let filePath = req.url === '/' ? '/prueba2.html' : req.url;
    filePath = path.join(__dirname, filePath.replace(/^\//, ''));
    fs.readFile(filePath, (err, data) => {
      if (err) { res.writeHead(404); res.end('Not found'); return; }
      const ext = path.extname(filePath).toLowerCase();
      const map = {'.html':'text/html', '.css':'text/css', '.js':'application/javascript', '.png':'image/png', '.jpg':'image/jpeg'};
      res.writeHead(200, {'Content-Type': map[ext] || 'application/octet-stream'});
      res.end(data);
    });
    return;
  }

  if (req.method === 'POST' && req.url === '/submit') {
    let body = '';
    req.on('data', chunk => body += chunk.toString());
    req.on('end', () => {
      try {
        const obj = JSON.parse(body);
        const line = JSON.stringify({receivedAt: new Date().toISOString(), ...obj});
        fs.appendFile(registrosPath, line + '\n', err => {
          if (err) { console.error('append error', err); res.writeHead(500); res.end(JSON.stringify({ok:false, error:'write-failed'})); return; }
          res.writeHead(200, {'Content-Type':'application/json'});
          res.end(JSON.stringify({ok:true}));
        });
      } catch (e) {
        res.writeHead(400, {'Content-Type':'application/json'});
        res.end(JSON.stringify({ok:false, error:'invalid-json'}));
      }
    });
    return;
  }

  res.writeHead(404); res.end('Not found');
});

server.listen(PORT, () => console.log(`Servidor en http://localhost:${PORT}`));
