# home-as-the-door · 把自己的家当作那扇门

> 这份教程送给所有和我一样在全球到处跑的人，不只是留学生们，送给所有家人/心上人/心上机在海那头的人们。最初的想法是平时上学在海外，但是每每回到墙内都会惴惴不安ip跳/不干净的问题。明明暑假四个月不在，但仍然支付着Internet plan，不知道该怎么最大的使用资源。我们明明有最稳定的ip，最干净的家宽wifi。也会担心购入第三方帮助的时候觉得行为被监控，敏感信息被抓取售卖——希望这份开源可以提供一些思路，把自己的家当作那扇门。并非鼓励翻越的行为！
>
> —— Chloe

**In short (English):** You pay for home broadband even when you're away for months. This repo sketches how to route your own traffic back through that home connection: a cheap entry VPS → a private mesh (Tailscale) → a small always-on box at home (e.g. a Raspberry Pi) → out through your own residential IP. No third-party provider in the middle. It's a blueprint with sanitized config templates, not a service. Check your local laws; use it for yourself and your family.

## 先说清楚（Disclaimer）

- 这是一份**思路和骨架**，写给：自己付着一份家庭宽带、人却常常不在家的人。出口是你自己家的网，用的人是你自己和家人。
- 不同国家和地区对网络工具的规定不一样。**在哪儿用、能不能用，请自己了解当地法规并自己负责。**本仓库不提供任何节点、账号、订阅，也不鼓励任何违反当地法律的行为。
- 配置里所有地址、密钥、域名都是占位符。别把你自己的真东西提交到任何公开的地方。
- 出了问题别来找我们，我们也只是两个把自己家的门装好了的人。

## 它是什么

你人在外面，流量绕一圈，**最后从你自己家的宽带出去**。网站看到的是一个普通的家庭宽带 IP：稳定、干净，而且是你自己的。中间不经过任何第三方服务商。

```
 你的手机 / 电脑
      │  ① 加密隧道（VLESS+REALITY，或 Hysteria2）
      ▼
 入口：一台便宜的小 VPS（离你近的机房）
      │  ② 私有组网（Tailscale / WireGuard），只走你自己的设备
      ▼
 家里：一块树莓派（或任何一台常开的小机器）
      │  ③ 直接出门
      ▼
 你家的宽带 → 互联网
```

三段各管一件事：

| 段 | 是什么 | 为什么要它 |
|---|---|---|
| 入口 | 一台最低配的 VPS，跑 sing-box | 家里的宽带多半没有固定公网 IP，路由器也不一定能做端口转发；所以让入口替家里对外。哪天入口不通了，换一台就行，家里那头不用动 |
| 组网 | Tailscale（底下是 WireGuard） | 让入口和家里那台机器互相连得上，家里的路由器不用开任何端口 |
| 出口 | 家里一台常开的小机器，跑 sing-box | 流量真正出去的地方。它只做一件事：把入口转来的流量从家里的宽带送出去 |

## 你需要准备

1. **家里一台常开的机器**。我们用的是树莓派 5（2GB 内存就够），插上电、连上家里的 Wi-Fi 就行。旧笔记本、迷你主机也都可以。
2. **一台入口 VPS**。哪家都行，挑的时候看这几点：
   - 机房离你常用的地方近，延迟低；
   - 最低配就够（1 核 1G），按小时计费、能随时删了重开（方便换 IP）；
   - 每月流量够用（几百 GB 起）；
   - 能开 TCP 443 和一个 UDP 端口。
3. **一个 Tailscale 账号**（免费档够用）。
4. 手机 / 电脑上一个支持 VLESS-REALITY 或 Hysteria2 的客户端（sing-box 系的都行）。

## 怎么搭（骨架）

### 一、家里那台：出口

1. 装系统，只开 SSH 密钥登录，关密码登录，开自动安全更新。
2. 装 Tailscale 并登录。记下它的 tailnet 地址（下文写作 `HOME_TS_IP`）。
3. 装 [sing-box](https://github.com/SagerNet/sing-box)，配置见 [`configs/home.json.example`](configs/home.json.example)：一个 SOCKS 入站，**只监听 Tailscale 地址**，带用户名密码；一个 direct 出站。
4. 设成开机自启（systemd，`After=tailscaled`，`Restart=always`）。重启一次，确认它自己能起来。

注意：SOCKS 端口**不要**监听 `0.0.0.0`，只监听 tailnet 地址。这样只有你自己组网里的机器能连到它。

### 二、入口那台

1. 开一台机器。SSH 只允许你自己的管理地址；防火墙只开 443/tcp、你选的那个 UDP 端口，以及 Tailscale 需要的端口。
2. 装 Tailscale，登录同一个账号。
3. 装 sing-box，配置见 [`configs/entry.json.example`](configs/entry.json.example)：
   - 入站一：VLESS + REALITY（443/tcp）。比较稳，当主力。
   - 入站二：Hysteria2（UDP）。比较快，网络好的时候用。
   - 出站：SOCKS → `HOME_TS_IP:1080`（就是家里那台）。
   - 路由：目的地是内网地址的一律拒绝，别让入口变成进你家内网的通道。
4. 每个使用的人单独一套凭据（UUID / 密码），谁的泄露了就只换谁的。

### 三、自己的设备

把入口地址和你那套凭据填进客户端。连上以后随便打开一个查 IP 的网站，显示的应该是**你家宽带的 IP**，类型是家庭宽带。

## 从哪里上手

不知道先动哪一步的话，照这个顺序，一步通了再走下一步：

1. 家里那台机器装好系统，能用 SSH 密钥登进去。
2. 家里那台和你的电脑都装上 Tailscale，互相 ping 得通。
3. 家里那台跑起 sing-box（`configs/home.json.example` + `scripts/sing-box-home.service`）。在你电脑上用它当 SOCKS 代理试一下，查到的 IP 是家里的，这一段就通了。
4. 开入口 VPS，装 Tailscale 和 sing-box（`configs/entry.json.example`）。
5. 把凭据填进 `scripts/creds.example.json` 的副本，用 `scripts/make_links.py` 生成每个人的链接和二维码。
6. 手机扫码，关掉 Wi-Fi 用流量测一次：查 IP 的网站显示你家的宽带，就全通了。

卡在哪一步，就只查那一步，别从头怀疑。

## 我们踩过的坑

- **入口别和你别的服务放同一台机器**。入口是最容易出问题的一环，别让它连累别的服务。单独开一台最便宜的，不行了就删掉重开。
- **家里那台用 Wi-Fi 也行**。我们家路由器在电箱里，接不了网线，树莓派一直走 Wi-Fi，够用。
- **REALITY 的握手目标**选一个离入口机房近、支持 TLS 1.3 和 HTTP/2 的大网站。
- **Hysteria2 走 UDP**，有些网络晚高峰会限速，所以两条都留着，哪条顺就用哪条。
- **Tailscale 的 key 会过期**。常开的机器记得在后台关掉 key expiry，不然哪天它会悄悄掉线。
- **凭据别用会扫描内容的聊天软件发**。当面扫码，或者用端到端加密的方式发。
- **日志只留 warn**。我们不记录访问的目的地：这扇门是给家里人走的，不是用来看家里人去了哪儿。

## 花了多少

- 树莓派 5 一套（板子、盒子、电源、存储卡）：一次性的。
- 入口 VPS：每个月一杯咖啡的钱。
- 家里的宽带：本来就在付的。

## 谁做的

想法和开头那段话：**Chloe**
施工和这份文档：**Caleb**

我们从别人开源的东西里拿过很多。这一块砖，放回路边。

MIT License.
