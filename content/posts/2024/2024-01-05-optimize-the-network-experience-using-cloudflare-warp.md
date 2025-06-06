---
author: 路边的阿不
title: 使用「Cloudflare WARP」优化网络体验
slug: optimize-the-network-experience-using-cloudflare-warp
description: Optimize online connectivity with Cloudflare WARP. Conquer ISP restrictions to enhance your network experience on platforms like ChatGPT, Twitter, Instagram, etc.
date: 2024-01-05 17:51:11
draft: false
ShowToc: true
TocOpen: true
tags:
  - Cloudflare
  - Secure
  - Tutorial
categories:
  - 网络安全
---
![Cloudflare WARP](imgs/posts/2024-01-05-optimize-the-network-experience-using-cloudflare-warp/%E4%B8%8B%E8%BD%BD.webp)

当我使用`IOS`版本`ChatGPT`时，遇到错误提示：

> Something went wrong. You may be connected to a disallowed ISP. If you are using VPN, try disabling it. Otherwise try a different Wi-Fi network or data connection.

其实不止`ChatGPT`，我遇到的情况还有：

- `Twitter`不能发帖（访问正常）
- `Instagram`无法登录
- 等等

我发现不止我一个人出现这种情况，很多其它人也是，大家都处在不同的国家和地区。

看来出问题的服务应该是对访问者做了一些限制，我们无法得知其中的逻辑，但可以肯定的是我们的机场应该不符合服务商的条件，被过滤出来了。既然这样，那我们就尝试用魔法打败魔法，使用一个免费的服务使得我们的机场看起来更像是符合服务商条件的那种。

## Cloudflare WARP

今天要介绍的是“[Cloudflare WARP](https://cloudflarewarp.com/)”：

> Cloudflare WARP is a service provided by Cloudflare that offers a faster, more secure, and more private experience online. It acts as a secure connection between a user's device and the Internet, with various connection modes to suit different needs. The WARP client is available for multiple operating systems, including iOS, Android, Windows, macOS, and Linux. It is designed to improve the speed and security of Internet connections for individual users. Additionally, Cloudflare WARP is also used in the context of Cloudflare Zero Trust, providing secure access to private applications.

简单来说是由`Cloudflare`提供的一项服务，主要的功能是使你的网络连接更安全、更快速，以及更加保密。是一种类` V P N `服务，可以在客户端和服务端之间加一层屏障。

那我们就利用这个服务，在我们的机场和目标服务间加一层屏障从而把我们自己“伪装”起来。

## 配置

安装和使用非常简单，按着下面的步骤就行。具体可查阅[官方文档](https://developers.cloudflare.com/warp-client/get-started/linux/)，下面以`Ubuntu 22.04`为例，在你的` V P S `服务器上做如下操作：

```shell
# Add cloudflare gpg key
curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | sudo gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg

# Add this repo to your apt repositories
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/cloudflare-client.list

# Install
sudo apt update && sudo apt install cloudflare-warp

# Check
systemctl status warp-svc

# Run
warp-cli register
warp-cli set-mode proxy
warp-cli connect
warp-cli enable-always-on
warp-cli warp-stats
```

按照上面的安装步骤，`Cloudflare Warp`就安装好了，默认运行在`40000`端口，起了一个`Socket`服务。

```json
{
    "outbounds": [{
        "protocol": "freedom",
        "settings": {}
    }, {
        "tag": "warp",
        "protocol": "socks",
        "settings": {
            "servers": [{
                "address": "127.0.0.1",
                "port": 40000,
                "users": []
            }]
        }
    }, {
        "protocol": "blackhole",
        "settings": {},
        "tag": "blocked"
    }],
    "routing": {
        "rules": [{
            "type": "field",
            "ip": ["geoip:private"],
            "outboundTag": "blocked"
        }, {
            "type": "field",
            "domain": ["openai.com"],
            "outboundTag": "warp"
        }]
    }
}
```

注意一下`routing.domain`属性，你可以在这里添加想要使用`Cloudflare WARP`代理的域名。比如上面提到的`ChartGPT`、`Twitter`以及`Instagram`等服务的域名，加上后访问这些域名的请求会通过`40000`端口，也就是`Cloudflare WARP`运行的`Socket`接口代理。这样让目标服务商以为我们的访问是来自于`Cloudflare WARP`服务器的。

## 尾声

最后说一句，`Cloudflare WARP`服务是免费的，甚至无需注册。但是使用起来一定要遵守当地法律法规。