/* eslint-disable no-underscore-dangle */
import { ExtensionContext, StatusBarItem, ThemeColor, workspace } from "vscode";
import { Capability, isCapabilityEnabled } from "../capabilities/capabilities";
import {
  FULL_BRAND_REPRESENTATION,
  STATUS_BAR_FIRST_TIME_CLICKED,
} from "../globals/consts";
import Config from "../workspaceConfig";


// decalre serverAlive as global variable
export let serverAlive = true;
export function setServerAlive(value: boolean) {
  serverAlive = value;
}

export function getStatusBarBackgroundColor(): ThemeColor | undefined {
  const config: Config = workspace.getConfiguration("StarCoderZZ") as Config;
  const { enbale } = config;
  if (!enbale) {
    return new ThemeColor("statusBarItem.warningBackground");
  }
  if (!serverAlive) {
    return new ThemeColor("statusBarItem.errorBackground");
  }
  return undefined;
}

export function getStatusBarText(): string {
  const config: Config = workspace.getConfiguration("StarCoderZZ") as Config;
  const { enbale } = config;
  if (!enbale) {
    return `${FULL_BRAND_REPRESENTATION}(Disabled)`;
  }
  if (!serverAlive) {
    return `${FULL_BRAND_REPRESENTATION}(Server disconnected)`;
  }
  return `${FULL_BRAND_REPRESENTATION}`;
}


export default class StatusBarData {
  private _icon?: string;

  private _text?: string;

  constructor(
    private _statusBarItem: StatusBarItem,
    private _context: ExtensionContext,
  ) {
    workspace.onDidChangeConfiguration(this.handleConfigurationChange, this);
  }

  private handleConfigurationChange() {
    this._statusBarItem.text = `${FULL_BRAND_REPRESENTATION}`;
    this._statusBarItem.backgroundColor = getStatusBarBackgroundColor();
  }


  public set icon(icon: string | undefined | null) {
    this._icon = icon || undefined;
    this.updateStatusBar();
  }

  public get icon(): string | undefined | null {
    return this._icon;
  }

  public set text(text: string | undefined | null) {
    this._text = text || undefined;
    this.updateStatusBar();
  }

  public get text(): string | undefined | null {
    return this._text;
  }

  public set backgroundColor(color: ThemeColor | undefined | null) {
    this._statusBarItem.backgroundColor = color || undefined;
  }

  private updateStatusBar() {
    this._statusBarItem.text = `${this._text ?? ""} ${this._icon ?? ""}`;
    this._statusBarItem.tooltip =
      isCapabilityEnabled(Capability.SHOW_AGRESSIVE_STATUS_BAR_UNTIL_CLICKED) &&
        !this._context.globalState.get(STATUS_BAR_FIRST_TIME_CLICKED)
        ? "Click to switch running mode"
        : `${FULL_BRAND_REPRESENTATION} (Click to open settings)`;
  }
}
