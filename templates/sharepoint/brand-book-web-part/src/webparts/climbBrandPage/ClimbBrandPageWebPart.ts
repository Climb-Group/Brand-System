import { Version } from '@microsoft/sp-core-library';
import {
  type IPropertyPaneConfiguration,
  PropertyPaneDropdown,
  PropertyPaneTextField
} from '@microsoft/sp-property-pane';
import { BaseClientSideWebPart } from '@microsoft/sp-webpart-base';

import styles from './ClimbBrandPageWebPart.module.scss';
import * as strings from 'ClimbBrandPageWebPartStrings';
import { BRAND_PAGES } from './book/pages';
import { PAGE_PARAM, SLUG, showBookPage } from './book/bookView';

export interface IClimbBrandPageWebPartProps {
  page: string;
  bookUrl: string;
}

export default class ClimbBrandPageWebPart extends BaseClientSideWebPart<IClimbBrandPageWebPartProps> {
  private _shown: string = '';
  private _watch: number = 0;

  // SharePoint moves between pages without reloading, and the brand book menus only change the page address, so the
  // web part draws the page again whenever the address changes. Links between brand book pages stay on this page.
  protected onInit(): Promise<void> {
    // SharePoint changes the address itself when its menu links point at this page, without telling web parts.
    this._watch = window.setInterval(() => {
      if (this._shown && this._shown !== this._base() + this._slug()) {
        this.render();
      }
    }, 300);
    window.addEventListener('popstate', this._onPopState);
    this.domElement.addEventListener('click', this._onClick);
    return super.onInit();
  }

  protected onDispose(): void {
    window.clearInterval(this._watch);
    window.removeEventListener('popstate', this._onPopState);
    this.domElement.removeEventListener('click', this._onClick);
    super.onDispose();
  }

  private _onPopState = (): void => {
    this.render();
  };

  private _onClick = (e: MouseEvent): void => {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) {
      return;
    }
    const a = (e.target as HTMLElement).closest ? (e.target as HTMLElement).closest('a[href]') as HTMLAnchorElement : null;
    if (!a || a.target) {
      return;
    }
    const to = new URL(a.href, window.location.href);
    const slug = to.searchParams.get(PAGE_PARAM) || '';
    if (to.origin !== window.location.origin || to.pathname.toLowerCase() !== window.location.pathname.toLowerCase() || !SLUG.test(slug)) {
      return;
    }
    if (slug === this._slug() && to.hash) {
      return;
    }
    e.preventDefault();
    window.history.pushState(null, '', to.pathname + to.search + to.hash);
    this.render();
  };

  public render(): void {
    const base = this._base();
    const slug = this._slug();
    if (this._shown === base + slug) {
      return;
    }
    const moved = this._shown !== '';
    this._shown = base + slug;
    showBookPage(this.domElement, {
      base,
      slug,
      className: styles.climbBrandPage,
      statusClass: styles.status,
      loading: strings.Loading,
      failed: strings.LoadFailed
    }).then((ok) => {
      if (!ok) {
        this._shown = '';
      } else if (moved && window.location.hash.length < 2) {
        this.domElement.scrollIntoView();
      }
    }).catch(() => {
      this._shown = '';
    });
  }

  protected get dataVersion(): Version {
    return Version.parse('1.0');
  }

  protected onPropertyPaneFieldChanged(): void {
    this._shown = '';
  }

  protected getPropertyPaneConfiguration(): IPropertyPaneConfiguration {
    return {
      pages: [
        {
          header: { description: strings.PropertyPaneDescription },
          groups: [
            {
              groupName: strings.BasicGroupName,
              groupFields: [
                PropertyPaneDropdown('page', { label: strings.PageFieldLabel, options: BRAND_PAGES }),
                PropertyPaneTextField('bookUrl', {
                  label: strings.BookUrlFieldLabel,
                  description: strings.BookUrlFieldDescription
                })
              ]
            }
          ]
        }
      ]
    };
  }

  // The brand book folder, ending in a slash.
  private _base(): string {
    const set = (this.properties.bookUrl || '').trim();
    const url = set || this.context.pageContext.web.absoluteUrl + '/SiteAssets/BrandCentre/book/';
    return url.charAt(url.length - 1) === '/' ? url : url + '/';
  }

  private _slug(): string {
    const asked = new URLSearchParams(window.location.search).get(PAGE_PARAM) || '';
    if (SLUG.test(asked)) {
      return asked;
    }
    return SLUG.test(this.properties.page || '') ? this.properties.page : 'index';
  }
}
